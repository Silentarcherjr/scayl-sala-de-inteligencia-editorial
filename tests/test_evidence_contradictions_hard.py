"""C4: hard contradiction set ([SINTÉTICO], tests/evidence_hard_cases.py). A conflict requires the same
indicator + period + place + unit, both observed, across publications."""
from datetime import UTC, datetime

import pytest

from scayl.contracts import ClaimStatus, ConflictKind, EvidenceStatus, Topic
from scayl.evidence.assemble import build_event
from tests.evidence_hard_cases import CASES, CASES_POSTHOC, evaluate
from tests.factories import CUTOFF, news, quake


@pytest.mark.parametrize("case", CASES + CASES_POSTHOC, ids=lambda c: f"{c[0]}-{c[1]}")
def test_conflict_detection_matches_label(case):
    cid, _, items, quakes, expected, why = case
    assert all(i.sintetico and i.titulo.startswith("[SINTÉTICO]") for i in items)
    topic = Topic.EVENTOS_NATURALES if "ismo" in items[0].titulo else Topic.ECONOMIA
    e = build_event(f"EVT-{cid}", items, topic, 0.9, [], quakes, CUTOFF)
    assert bool(e.conflicts) is expected, why


def test_whole_set_has_no_false_positive_or_negative():
    result = evaluate()
    assert (result["fp"], result["fn"]) == (0, 0)


def test_semantic_conflict_keeps_both_versions_and_blocks_draft_status():
    items = next(c[2] for c in CASES if c[0] == "C19")
    e = build_event("EVT-S19", items, Topic.LOGISTICA_CANAL, 0.9, [], [], CUTOFF)
    c = e.conflicts[0]
    assert c.kind == ConflictKind.SEMANTIC and c.status == "sin_resolver"
    assert {c.version_a.evidence[0].evidence_id, c.version_b.evidence[0].evidence_id} == {"news:a", "news:b"}
    assert e.claims[0].status == ClaimStatus.EN_CONFLICTO
    assert e.evidence_status != EvidenceStatus.SUFICIENTE_PARA_BORRADOR


def test_correction_is_flagged_in_the_verification_note():
    items = next(c[2] for c in CASES if c[0] == "C11")
    e = build_event("EVT-S11", items, Topic.ECONOMIA, 0.9, [], [], CUTOFF)
    assert "corrección" in e.conflicts[0].verification_needed
    assert {e.conflicts[0].version_a.value, e.conflicts[0].version_b.value} == {"9.1%", "9.5%"}


def test_real_case_distant_quake_affecting_panama_is_not_a_version_of_a_local_quake():
    """Real snapshot (demo EVT-0114): a M7.4 Mexico-Guatemala quake 'sin riesgo de tsunami para Panamá' was
    reported as a magnitude conflict with a M4.7 Panamá-Costa Rica quake. Different quakes, no conflict."""
    t = datetime(2026, 7, 16, 18, tzinfo=UTC)
    items = [news("d8c3", "Sismo de magnitud 4.7 sacude la frontera entre Panamá y Costa Rica; no se reportan daños",
                  medio="telemetro.com", pub=None, det=t),
             news("c6b0", "Sismo de magnitud 7.4 entre México y Guatemala no genera riesgo de tsunami para Panamá",
                  medio="telemetro.com", pub=None, det=datetime(2026, 7, 17, 18, tzinfo=UTC))]
    e = build_event("EVT-R114", items, Topic.EVENTOS_NATURALES, 0.9, [], [quake("usR", 4.5, t)],
                    datetime(2026, 10, 1, tzinfo=UTC))
    assert [(c.version_a.value, c.version_b.value) for c in e.conflicts] == [("4.7", "4.5")]
