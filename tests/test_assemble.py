"""End-to-end evidence assembly on synthetic records: T02, T03, T04, T05, T08."""
from datetime import datetime, timedelta

from scayl.contracts import ClaimStatus, EvidenceStatus, PriorityTier, Topic
from scayl.evidence.assemble import build_event
from scayl.gen.template import build_template_package
from scayl.gen.validators import SCOPE_PHRASE
from tests.factories import CUTOFF, UTC, news, quake, wb

T = datetime(2025, 9, 30, 3, 0, tzinfo=UTC)


def test_t02_three_records_same_event_do_not_triple_importance():
    one = build_event("EVT-0001", [news("a", "Sismo de magnitud 4.6 sacude Chiriquí (EFE)", medio="x.com")],
                      Topic.EVENTOS_NATURALES, 0.9, [], [], CUTOFF)
    three = build_event("EVT-0001", [news(i, "Sismo de magnitud 4.6 sacude Chiriquí (EFE)", medio=f"{i}.com")
                                     for i in "abc"], Topic.EVENTOS_NATURALES, 0.9, [], [], CUTOFF)
    assert three.source_dna.publications == 3 and three.source_dna.max_possible_independent == 1
    assert three.priority.score == one.priority.score


def test_seismic_headline_supported_by_usgs_and_damage_unsupported():
    items = [news("a", "Sismo de magnitud 4.6 sacude Chiriquí", pub=T)]
    e = build_event("EVT-0002", items, Topic.EVENTOS_NATURALES, 0.9, [], [quake("us1", 4.6, T - timedelta(hours=1))],
                    CUTOFF)
    statuses = {c.statement: c.status for c in e.claims}
    assert any(s == ClaimStatus.SUSTENTADA and "4.6" in k for k, s in statuses.items())
    assert statuses["El sismo causó daños o personas afectadas"] == ClaimStatus.SIN_SUSTENTO
    assert e.evidence_status == EvidenceStatus.SUFICIENTE_PARA_BORRADOR
    pkg = build_template_package(e)
    assert pkg.validation.passed and pkg.scope_disclaimer == SCOPE_PHRASE


def test_usgs_not_linked_when_time_or_magnitude_do_not_match():
    items = [news("a", "Sismo de magnitud 4.6 sacude Chiriquí", pub=T)]
    far = build_event("EVT-0003", items, Topic.EVENTOS_NATURALES, 0.9, [], [quake("us1", 4.6, T - timedelta(days=5))],
                      CUTOFF)
    wrong = build_event("EVT-0003", items, Topic.EVENTOS_NATURALES, 0.9, [], [quake("us2", 5.5, T)], CUTOFF)
    assert not far.official_evidence and not wrong.official_evidence


def test_t03_recirculated_story_keeps_original_date():
    old = news("a", "Panamá inaugura puerto", pub=datetime(2024, 3, 1, tzinfo=UTC), det=datetime(2025, 9, 29, tzinfo=UTC))
    e = build_event("EVT-0004", [old], Topic.LOGISTICA_CANAL, 0.8, [], [], CUTOFF)
    assert e.is_recirculated and e.first_published.year == 2024
    assert e.priority.components.U < 0.01


def test_t04_world_bank_is_historical_context_with_warning():
    obs = [wb("FP.CPI.TOTL.ZG", 2023, 1.5), wb("FP.CPI.TOTL.ZG", 2024, 0.7), wb("FP.CPI.TOTL.ZG", 2025, None)]
    e = build_event("EVT-0005", [news("a", "Debate sobre la inflación en Panamá")], Topic.ECONOMIA, 0.8, obs, [],
                    CUTOFF)
    ref = next(r for r in e.official_evidence if r.evidence_id.startswith("wb:"))
    assert ref.evidence_id == "wb:PAN:FP.CPI.TOTL.ZG:2024" and ref.value == 0.7 and ref.period == "2024"
    assert any("Dato histórico — 2024" in w.message for w in e.temporal_warnings)
    assert e.evidence_status == EvidenceStatus.PARCIAL  # context, not confirmation


def test_t05_incompatible_figures_are_both_shown_and_unresolved():
    items = [news("a", "Inflación en Panamá sube a 1.2%", medio="x.com"),
             news("b", "Inflación en Panamá llega a 2.1%", medio="y.com")]
    e = build_event("EVT-0006", items, Topic.ECONOMIA, 0.8, [], [], CUTOFF)
    assert len(e.conflicts) == 1
    c = e.conflicts[0]
    assert {c.version_a.value, c.version_b.value} == {"1.2%", "2.1%"} and c.status == "sin_resolver"
    assert e.evidence_status != EvidenceStatus.SUFICIENTE_PARA_BORRADOR
    assert any(cl.status == ClaimStatus.EN_CONFLICTO for cl in e.claims)


def test_t08_high_priority_insufficient_evidence_recommends_investigation():
    e = build_event("EVT-0007", [news("a", "Canal de Panamá anuncia cierre de esclusas", pub=CUTOFF - timedelta(hours=3))],
                    Topic.LOGISTICA_CANAL, 0.95, [], [], CUTOFF)
    assert e.priority.tier == PriorityTier.ALTO
    assert e.evidence_status == EvidenceStatus.INSUFICIENTE
    assert "NO habilita publicación" in e.recommended_action
    assert len(e.gap.investigate_next) == 3


def test_gdelt_items_without_publication_date_still_rank_by_detection():
    det = CUTOFF - timedelta(hours=4)
    e = build_event("EVT-0020", [news("g", "Canal de Panamá anuncia ajustes de calado", pub=None, det=det)],
                    Topic.LOGISTICA_CANAL, 0.9, [], [], CUTOFF)
    assert e.first_published is None and e.first_detected == det  # publication stays unknown
    assert e.priority.components.U > 0.8 and not e.is_recirculated


def test_real_case_headline_denying_a_quake_is_not_confirmed_by_usgs():
    """Real snapshot case (EVT-0183): 'IGUP descarta ... algún temblor' must not become SUSTENTADA."""
    items = [news("n", "Sismo en Panamá hoy: IGUP descarta que se haya registrado algún temblor", pub=T)]
    e = build_event("EVT-0030", items, Topic.EVENTOS_NATURALES, 0.9, [], [quake("us3", 3.6, T - timedelta(hours=5))],
                    CUTOFF)
    assert e.claims[0].status == ClaimStatus.SOLO_REPORTADA  # central claim = the headline, unconfirmed
    ctx = [c for c in e.claims if "NO confirma" in c.reason]
    assert ctx and ctx[0].status == ClaimStatus.SUSTENTADA
    assert e.evidence_status != EvidenceStatus.SUFICIENTE_PARA_BORRADOR


def test_real_case_magnitude_mismatch_with_usgs_is_a_visible_conflict():
    """Real snapshot case (EVT-0125): headline 4.7 vs USGS 4.5 -> linked, but conflict shown."""
    items = [news("m", "Sismo de magnitud 4.7 sacude la frontera entre Panamá y Costa Rica", pub=T)]
    e = build_event("EVT-0031", items, Topic.EVENTOS_NATURALES, 0.9, [], [quake("us4", 4.5, T)], CUTOFF)
    assert e.claims[0].status == ClaimStatus.SUSTENTADA and "4.5" in e.claims[0].statement
    assert len(e.conflicts) == 1 and {e.conflicts[0].version_a.value, e.conflicts[0].version_b.value} == {"4.7", "4.5"}
    assert e.evidence_status == EvidenceStatus.PARCIAL
