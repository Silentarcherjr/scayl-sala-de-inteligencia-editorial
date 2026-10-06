"""T02 / jury question: 'if five outlets replicate one agency, how many independent sources?'"""
from scayl.contracts import ProvenanceLabel
from scayl.evidence.provenance import NO_INDEPENDENCE, source_dna
from tests.factories import news


def test_five_outlets_replicating_one_agency_count_as_one_provenance():
    items = [news(f"n{i}", f"Panamá aprueba nueva ley de puertos (EFE) versión {i}", medio=f"m{i}.com")
             for i in range(5)]
    dna = source_dna(items)
    assert dna.publications == 5 and dna.outlets == 5
    assert dna.max_possible_independent == 1
    assert dna.groups[0].label == ProvenanceLabel.PROCEDENCIA_COMUN_IDENTIFICADA
    assert "EFE" in dna.groups[0].basis
    assert dna.confirmed_independent == 0 and dna.statement == NO_INDEPENDENCE


def test_identical_headlines_collapse_and_same_outlet_is_one_source():
    items = [news("a", "Sismo sacude Chiriquí", medio="x.com"), news("b", "Sismo sacude Chiriquí", medio="y.com"),
             news("c", "Otra nota del mismo medio", medio="z.com"), news("d", "Segunda nota", medio="z.com")]
    dna = source_dna(items)
    labels = sorted(g.label.value for g in dna.groups)
    assert labels == ["mismo_medio", "procedencia_comun_identificada"]
    assert dna.max_possible_independent == 2


def test_distinct_outlets_without_evidence_are_unknown_never_confirmed():
    items = [news("a", "Lluvias afectan Darién", medio="x.com"), news("b", "Inundaciones en Darién", medio="y.com")]
    dna = source_dna(items)
    assert {g.label for g in dna.groups} == {ProvenanceLabel.INDEPENDENCIA_DESCONOCIDA}
    assert dna.confirmed_independent == 0
