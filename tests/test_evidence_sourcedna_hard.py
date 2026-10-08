"""C2: Source DNA counts and wire-copy duplicates (all records synthetic)."""
from collections import Counter

from scayl.contracts import EvidenceStatus, ProvenanceLabel, Topic
from scayl.evidence.assemble import build_event
from scayl.evidence.provenance import NO_INDEPENDENCE, source_dna
from tests.factories import CUTOFF, news, recent

P = "[SINTÉTICO] "


def _counts(dna):
    labels = Counter(g.label for g in dna.groups)
    return {"publications": dna.publications, "outlets": dna.outlets,
            "common_origin_groups": labels[ProvenanceLabel.PROCEDENCIA_COMUN_IDENTIFICADA],
            "same_outlet_groups": labels[ProvenanceLabel.MISMO_MEDIO],
            "unknown_independence": labels[ProvenanceLabel.INDEPENDENCIA_DESCONOCIDA],
            "confirmed_independent": dna.confirmed_independent, "max_possible": dna.max_possible_independent}


def test_counts_distinguish_articles_outlets_common_origin_and_unknown():
    items = [news("a", P + "Canal de Panamá ajusta calado (EFE)", medio="x.com"),
             news("b", P + "Canal de Panamá ajusta calado, según EFE", medio="y.com"),
             news("c", P + "Canal ajusta calado por sequía", medio="z.com"),
             news("d", P + "Navieras reaccionan al nuevo calado", medio="z.com"),
             news("e", P + "Calado del Canal: lo que se sabe", medio="w.com")]
    assert _counts(source_dna(items)) == {
        "publications": 5, "outlets": 4, "common_origin_groups": 1, "same_outlet_groups": 1,
        "unknown_independence": 1, "confirmed_independent": 0, "max_possible": 3}


def test_wire_copies_do_not_raise_corroboration_score_or_status():
    one = [news("a", P + "Lluvias causan inundaciones en Darién (AFP)", medio="x.com")]
    many = one + [news(n, P + "Lluvias causan inundaciones en Darién (AFP)", medio=f"{n}.com") for n in "bcdef"]
    e1 = build_event("EVT-D01", one, Topic.EVENTOS_NATURALES, 0.9, [], [], CUTOFF)
    e6 = build_event("EVT-D06", many, Topic.EVENTOS_NATURALES, 0.9, [], [], CUTOFF)
    assert e6.source_dna.publications == 6 and e6.source_dna.max_possible_independent == 1
    assert e6.priority.components.E == e1.priority.components.E
    assert e6.priority.score == e1.priority.score
    assert e6.evidence_status == e1.evidence_status == EvidenceStatus.INSUFICIENTE
    assert e6.source_dna.statement == NO_INDEPENDENCE


def test_syndicated_copies_with_outlet_suffix_collapse():
    items = [news("a", P + "Panamá aprueba ley de puertos - La Prensa", medio="x.com"),
             news("b", P + "Panamá aprueba ley de puertos | Telemetro", medio="y.com")]
    dna = source_dna(items)
    assert dna.max_possible_independent == 1
    assert dna.groups[0].label == ProvenanceLabel.PROCEDENCIA_COMUN_IDENTIFICADA


def test_mobile_and_amp_editions_are_the_same_outlet():
    items = [news("a", P + "Sismo sacude Chiriquí", medio="www.diario.com"),
             news("b", P + "Réplica en Chiriquí", medio="m.diario.com"),
             news("c", P + "Daños menores en Boquete", medio="amp.diario.com")]
    dna = source_dna(items)
    assert dna.outlets == 1 and dna.max_possible_independent == 1
    assert dna.groups[0].label == ProvenanceLabel.MISMO_MEDIO


def test_official_sources_are_counted_apart_from_publications():
    obs = [recent("ACP.GATUN.NIVEL", "2025-09-28", 86.4, "acp", "pies")]
    items = [news("a", P + "Lago Gatún sube a 86,4 pies y el Canal mantiene calado")]
    e = build_event("EVT-D07", items, Topic.LOGISTICA_CANAL, 0.9, obs, [], CUTOFF)
    assert e.source_dna.publications == 1 and e.source_dna.confirmed_independent == 0
    assert [r.evidence_id for r in e.official_evidence] == ["ind:acp:ACP.GATUN.NIVEL:2025-09-28"]
