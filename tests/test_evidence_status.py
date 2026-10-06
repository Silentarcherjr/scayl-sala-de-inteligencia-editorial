from scayl.contracts import EvidenceStatus
from scayl.evidence.status import evidence_status


def test_supported_central_claim_is_sufficient(events):
    e = events["EVT-0001"]
    status, _ = evidence_status(e.claims, e.conflicts, e.official_evidence, e.source_dna)
    assert status == EvidenceStatus.SUFICIENTE_PARA_BORRADOR


def test_unresolved_conflict_caps_at_partial(events):
    e = events["EVT-0002"]
    status, reason = evidence_status(e.claims, e.conflicts, e.official_evidence, e.source_dna)
    assert status == EvidenceStatus.PARCIAL and "conflicto" in reason


def test_single_source_without_official_is_insufficient(events):
    e = events["EVT-0003"]
    status, _ = evidence_status(e.claims, e.conflicts, e.official_evidence, e.source_dna)
    assert status == EvidenceStatus.INSUFICIENTE
