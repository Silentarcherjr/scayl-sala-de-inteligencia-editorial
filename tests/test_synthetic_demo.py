from pathlib import Path

from scayl.contracts import ClaimStatus, EvidenceStatus
from scayl.ingest.synthetic_demo import replay


def test_synthetic_cases_exercise_existing_guards_without_real_corpus():
    bundle, report = replay(Path("data/synthetic/cases.jsonl"))
    events = {event.event_id.removeprefix("EVT-SYN-"): event for event in bundle.events}
    assert all(item.sintetico and item.titulo.startswith("[SINTÉTICO]") for item in bundle.news)
    assert all(event.synthetic for event in bundle.events)
    invalid = next(item for item in bundle.news if item.id_noticia == "SYN-T01")
    assert invalid.fecha_publicacion is None
    assert "fecha_invalida:fecha_publicacion" in invalid.quality_flags
    assert events["T02"].source_dna.publications == 3
    assert events["T02"].source_dna.confirmed_independent == 0
    assert any(len(group.member_ids) == 2 for group in events["T02"].source_dna.groups)
    assert events["T03"].is_recirculated
    assert events["T03"].first_published.year == 2024
    assert events["T03"].first_detected.year == 2025
    assert events["T05"].conflicts
    assert any(claim.status == ClaimStatus.EN_CONFLICTO for claim in events["T05"].claims)
    assert events["T07"].security_flags
    assert events["SUFICIENTE"].evidence_status == EvidenceStatus.SUFICIENTE_PARA_BORRADOR
    assert events["SUFICIENTE"].claims[0].status == ClaimStatus.SUSTENTADA
    assert len(report["cases"]) == 6
