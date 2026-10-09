"""C3: Temporal Guard and official linking under hard cases (all records synthetic)."""
from datetime import UTC, datetime, timedelta

from scayl.contracts import ClaimStatus, EvidenceStatus, Topic
from scayl.evidence.assemble import build_event
from tests.factories import news, quake, recent, wb

CUT = datetime(2026, 10, 1, tzinfo=UTC)
T = datetime(2026, 9, 29, 12, tzinfo=UTC)
P = "[SINTÉTICO] "


def test_world_bank_2024_value_never_confirms_a_2026_headline_even_with_the_same_figure():
    item = news("w1", P + "Inflación en Panamá es de 0,7% en 2026", pub=T)
    e = build_event("EVT-T01", [item], Topic.ECONOMIA, 0.9, [wb("FP.CPI.TOTL.ZG", 2024, 0.7)], [], CUT)
    assert e.claims[0].status == ClaimStatus.SOLO_REPORTADA
    assert not any(c.status == ClaimStatus.SUSTENTADA and any(r.evidence_id.startswith("wb:") for r in c.evidence)
                   for c in e.claims)
    assert any("Dato histórico — 2024" in w.message for w in e.temporal_warnings)
    assert e.evidence_status != EvidenceStatus.SUFICIENTE_PARA_BORRADOR


def test_usgs_quake_near_in_time_but_in_another_country_neither_confirms_nor_contextualises():
    item = news("q1", P + "Sismo de magnitud 4.6 sacude Chiriquí", pub=T)
    far = quake("usCR", 4.6, T - timedelta(hours=2), place="120 km SW of Jacó, Costa Rica")
    e = build_event("EVT-T02", [item], Topic.EVENTOS_NATURALES, 0.9, [], [far], CUT)
    assert not e.official_evidence
    assert e.claims[0].status == ClaimStatus.SOLO_REPORTADA
    assert e.evidence_status != EvidenceStatus.SUFICIENTE_PARA_BORRADOR


def test_usgs_quake_near_in_time_with_other_magnitude_does_not_confirm():
    item = news("q2", P + "Sismo de magnitud 4.6 sacude Chiriquí", pub=T)
    e = build_event("EVT-T03", [item], Topic.EVENTOS_NATURALES, 0.9, [], [quake("usX", 5.4, T)], CUT)
    assert not any(c.status == ClaimStatus.SUSTENTADA for c in e.claims)


def test_border_quake_named_in_both_countries_is_still_linked():
    item = news("q3", P + "Sismo de magnitud 4.6 sacude la frontera entre Panamá y Costa Rica", pub=T)
    q = quake("usB", 4.6, T - timedelta(hours=1), place="25 km S of Punta Burica, Costa Rica")
    e = build_event("EVT-T04", [item], Topic.EVENTOS_NATURALES, 0.9, [], [q], CUT)
    assert e.claims[0].status == ClaimStatus.SUSTENTADA


def test_acp_projection_never_confirms_a_headline_with_the_same_figure():
    proj = recent("ACP.GATUN.PROYECCION", "2026-10-15", 85.0, "acp", "pies", proj=True)
    item = news("p1", P + "Lago Gatún bajará a 85 pies, advierte el Canal", pub=T)
    e = build_event("EVT-T05", [item], Topic.LOGISTICA_CANAL, 0.9, [proj], [], CUT)
    assert e.claims[0].status == ClaimStatus.SOLO_REPORTADA
    assert e.evidence_status != EvidenceStatus.SUFICIENTE_PARA_BORRADOR


def test_observation_never_confirms_a_headline_that_is_a_forecast():
    obs = recent("ACP.GATUN.NIVEL", "2026-09-28", 86.4, "acp", "pies")
    item = news("p2", P + "ACP proyecta que el lago Gatún bajará a 86,4 pies en el canal", pub=T)
    e = build_event("EVT-T06", [item], Topic.LOGISTICA_CANAL, 0.9, [obs], [], CUT)
    assert e.claims[0].status == ClaimStatus.SOLO_REPORTADA  # observed value is context only
    assert e.evidence_status != EvidenceStatus.SUFICIENTE_PARA_BORRADOR


def test_panama_cpi_never_confirms_or_contextualises_another_country():
    inec = recent("INEC.IPC.VAR_MENSUAL", "2026-08", 0.3, "inec", "%")
    item = news("x1", P + "Inflación en Costa Rica sube 0,3% en agosto", pub=T)
    e = build_event("EVT-T07", [item], Topic.ECONOMIA, 0.9, [inec, wb("FP.CPI.TOTL.ZG", 2024, 0.7)], [], CUT)
    assert not e.official_evidence
    assert e.claims[0].status == ClaimStatus.SOLO_REPORTADA


def test_panama_cpi_still_confirms_a_matching_panama_headline():
    inec = recent("INEC.IPC.VAR_MENSUAL", "2026-08", 0.3, "inec", "%")
    item = news("x2", P + "Inflación en Panamá sube 0,3% en agosto", pub=T)
    e = build_event("EVT-T08", [item], Topic.ECONOMIA, 0.9, [inec], [], CUT)
    assert e.claims[0].status == ClaimStatus.SUSTENTADA
    assert "2026-08" in e.claims[0].evidence[0].period
