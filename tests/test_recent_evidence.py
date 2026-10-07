"""AP-010: recent official evidence (ACP Gatún levels, INEC monthly CPI) supports matching headlines."""
from datetime import UTC, datetime

from scayl.contracts import ClaimStatus, EvidenceStatus, Topic, UIBundle
from scayl.evidence.assemble import build_event
from scayl.gen.llm import LLM
from scayl.gen.qa import answer
from tests.factories import news, recent, wb

CUT = datetime(2026, 10, 1, tzinfo=UTC)
ACP = [recent("ACP.GATUN.NIVEL", "2026-09-27", 85.9, "acp", "pies"),
       recent("ACP.GATUN.NIVEL", "2026-09-28", 86.4, "acp", "pies"),
       recent("ACP.GATUN.NIVEL", "2026-09-30", 86.6, "acp", "pies"),
       recent("ACP.GATUN.PROYECCION", "2026-10-15", 85.0, "acp", "pies", proj=True),
       recent("ACP.GATUN.NIVEL", "2026-10-03", 99.0, "acp", "pies")]  # after cutoff: ignored
INEC = [recent("INEC.IPC.VAR_MENSUAL", "2026-06", 0.2, "inec", "%"),
        recent("INEC.IPC.VAR_MENSUAL", "2026-07", -0.3, "inec", "%")]


def test_headline_figure_matching_acp_observation_is_supported():
    item = news("c1", "Lago Gatún sube a 86,4 pies y el Canal mantiene calado", pub=datetime(2026, 9, 29, 9, tzinfo=UTC))
    e = build_event("EVT-0100", [item], Topic.LOGISTICA_CANAL, 0.9, ACP, [], CUT)
    central = e.claims[0]
    assert central.status == ClaimStatus.SUSTENTADA and "86.4" in central.statement
    assert central.evidence[0].evidence_id == "ind:acp:ACP.GATUN.NIVEL:2026-09-28"
    assert e.evidence_status == EvidenceStatus.SUFICIENTE_PARA_BORRADOR
    assert any("Proyección de la ACP" in w.message for w in e.temporal_warnings)
    assert not any("99.0" in c.statement for c in e.claims)  # post-cutoff data never used


def test_without_matching_figure_acp_is_context_only():
    item = news("c2", "Navieras preguntan por el calado del Canal", pub=datetime(2026, 9, 29, tzinfo=UTC))
    e = build_event("EVT-0101", [item], Topic.LOGISTICA_CANAL, 0.9, ACP, [], CUT)
    assert e.claims[0].status == ClaimStatus.SOLO_REPORTADA  # headline stays a media claim
    ctx = [c for c in e.claims if c.status == ClaimStatus.SUSTENTADA]
    assert ctx and "2026-09-30" in ctx[0].statement  # latest observation, with its date
    assert e.evidence_status == EvidenceStatus.PARCIAL
    assert all(not r.evidence_id.endswith("2026-10-15") or "proyección" in (r.excerpt or "")
               for r in e.official_evidence)


def test_inec_monthly_cpi_supports_recent_inflation_headline_and_wb_stays_historical():
    item = news("i1", "Inflación en Panamá: precios bajan 0,3% en julio", pub=datetime(2026, 8, 13, tzinfo=UTC))
    obs = INEC + [wb("FP.CPI.TOTL.ZG", 2024, 0.7)]
    e = build_event("EVT-0102", [item], Topic.ECONOMIA, 0.9, obs, [], CUT)
    assert e.claims[0].status == ClaimStatus.SUSTENTADA
    assert e.claims[0].evidence[0].evidence_id == "ind:inec:INEC.IPC.VAR_MENSUAL:2026-07"
    assert any(r.evidence_id == "wb:PAN:FP.CPI.TOTL.ZG:2024" for r in e.official_evidence)
    msgs = " ".join(w.message for w in e.temporal_warnings)
    assert "Dato histórico — 2024" in msgs and "Dato de 2026-07 (INEC)" in msgs


def test_qa_answers_recent_series_with_period():
    b = UIBundle(snapshot_version="t", snapshot_cutoff_utc=CUT, signals_total=0, signals_valid=0, events=[],
                 indicators=ACP + INEC)
    a = answer("¿Cuál fue el nivel del lago Gatún el 2026-09-28?", b, LLM(mode="template"))
    assert not a.abstained and a.citations[0].evidence_id.startswith("ind:acp:")
