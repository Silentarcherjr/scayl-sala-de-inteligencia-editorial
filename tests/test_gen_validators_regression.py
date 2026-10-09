"""Claim-vs-citation validators: the cited evidence must support what the sentence says, not just exist.

Each check has a positive case (removed, with its code) and a false-positive guard (kept).
"""
import pytest

from scayl.contracts import Claim, ClaimStatus, ClaimType, EvidenceKind, EvidenceRef, TaggedSentence
from scayl.gen.template import build_template_package
from scayl.gen.validators import _Ctx, check_sentence, validate_package


def claim(statement, status=ClaimStatus.SOLO_REPORTADA, period=None, value=None, cid="CLM-0950-001",
          kind=EvidenceKind.NEWS, field="titulo", who="medio-a.com"):
    ref = EvidenceRef(evidence_id="news:z1" if kind == EvidenceKind.NEWS else "wb:PAN:X:2023", kind=kind,
                      field=field, value=value if value is not None else statement, period=period,
                      excerpt=statement if kind == EvidenceKind.NEWS else None)
    return Claim(claim_id=cid, event_id="EVT-0950", statement=statement,
                 type=ClaimType.DECLARACION if status == ClaimStatus.SOLO_REPORTADA else ClaimType.HECHO,
                 status=status, attributed_to=who if status == ClaimStatus.SOLO_REPORTADA else None,
                 evidence=[ref], reason="test", extracted_by="rule")


def run(text, c, tag=ClaimType.DECLARACION):
    ctx = _Ctx(claims={c.claim_id: c})
    out = check_sentence(TaggedSentence(text=text, tag=tag, claim_ids=[c.claim_id]), ctx, "t")
    return out, [i.code for i in ctx.issues if i.severity == "error"]


HEAD = claim("Canal de Panamá reduce el tránsito de buques por El Niño")
PCT = claim("La inflación de Panamá fue 1.5% en 2023", status=ClaimStatus.SUSTENTADA, period="2023", value=1.5,
            kind=EvidenceKind.INDICATOR, field="valor")


@pytest.mark.parametrize("text,code", [
    ("Según medio-a.com, el Canal no reduce el tránsito de buques.", "NEGATION_FLIP"),
    ("Según medio-a.com, el Canal reduce el tránsito debido a una huelga.", "CAUSALITY_NOT_IN_EVIDENCE"),
    ("Según medio-a.com, el Canal reduce el tránsito; la Autoridad Marítima lo ordenó.", "ENTITY_NOT_IN_EVIDENCE"),
    ("Según medio-a.com, la ACP es culpable de la reducción del tránsito.", "ACCUSATION_NOT_IN_EVIDENCE"),
])
def test_unsupported_additions_to_a_headline_are_removed(text, code):
    out, codes = run(text, HEAD)
    assert out is None and codes == [code]


@pytest.mark.parametrize("text", [
    "Según medio-a.com, el Canal reduce el tránsito de buques por El Niño.",
    "Según medio-a.com, el Canal reduce el tránsito; la reducción no ha sido confirmada por fuentes oficiales.",
    "Según medio-a.com, el Canal reduce el tránsito; repetir el titular no prueba independencia.",
])
def test_faithful_or_hedged_sentences_are_kept(text):
    out, codes = run(text, HEAD)
    assert out is not None and codes == []


def test_causal_verb_without_causal_evidence_is_removed():
    c = claim("ACP anuncia ajustes de calado en el Canal")
    out, codes = run("Según medio-a.com, la sequía provocó los ajustes de calado de la ACP.", c)
    assert out is None and codes == ["CAUSALITY_NOT_IN_EVIDENCE"]
    # the cause named by the evidence itself is fine
    assert run("Según medio-a.com, el Canal reduce el tránsito debido a El Niño.", HEAD)[0] is not None


def test_dropped_negation_is_removed():
    c = claim("ACP no aplicará restricciones de calado este mes")
    out, codes = run("Según medio-a.com, la ACP aplicará restricciones de calado.", c)
    assert out is None and codes == ["NEGATION_FLIP"]
    assert run("Según medio-a.com, la ACP no aplicará restricciones de calado.", c)[0] is not None


def test_unit_mismatch_is_removed():
    c = claim("Construcción del puente presenta 39 metros de avance")
    out, codes = run("Según medio-a.com, el puente presenta un 39% de avance.", c)
    assert out is None and codes == ["UNIT_MISMATCH"]
    assert run("Según medio-a.com, el puente presenta 39 metros de avance.", c)[0] is not None


def test_percentage_vs_percentage_points_is_removed():
    c = claim("La tasa sube 2 puntos porcentuales")
    assert run("Según medio-a.com, la tasa sube 2%.", c)[1] == ["UNIT_MISMATCH"]


def test_level_presented_as_relative_change_is_removed():
    out, codes = run("La inflación de Panamá aumentó 1.5% en 2023.", PCT, tag=ClaimType.HECHO)
    assert out is None and codes == ["RELATIVE_CHANGE_UNSUPPORTED"]
    assert run("La inflación de Panamá fue 1.5% en 2023.", PCT, tag=ClaimType.HECHO)[0] is not None


def test_change_supported_by_evidence_is_kept():
    c = claim("Tarifas del Canal aumentan 16% en comparación a las del 2025")
    assert run("Según medio-a.com, las tarifas aumentan 16% respecto a 2025.", c)[0] is not None


def test_invented_percentage_is_removed():
    assert run("La inflación de Panamá fue 2.5% en 2023.", PCT, tag=ClaimType.HECHO)[1] == ["NUMBER_NOT_IN_EVIDENCE"]


@pytest.mark.parametrize("word", ["actualmente", "ahora", "en este momento", "a la fecha"])
def test_historical_value_phrased_as_current_is_removed(word):
    out, codes = run(f"La inflación de Panamá es {word} 1.5%, dato de 2023.", PCT, tag=ClaimType.HECHO)
    assert out is None and codes == ["TEMPORAL_PRESENT"]


def test_full_name_of_a_cited_surname_is_not_an_unsupported_entity():
    c = claim("Sheinbaum recibe a Mulino en Palacio Nacional")
    assert run("Según medio-a.com, Claudia Sheinbaum recibe a José Raúl Mulino.", c)[0] is not None
    assert run("Según medio-a.com, Sheinbaum recibe a Mulino. #CanalPanama #Logistica", c)[0] is not None


def test_absence_statement_about_causality_is_kept():
    c = claim("El sismo causó daños o personas afectadas", status=ClaimStatus.SIN_SUSTENTO)
    out, codes = run("No hay evidencia en el corpus de que el sismo causó daños.", c, tag=ClaimType.HECHO)
    assert out is not None and codes == []


def test_fixture_template_packages_still_validate_without_removals(events):
    """No-regression on the fixture: deterministic packages lose no sentence to the new checks."""
    new_codes = {"NEGATION_FLIP", "CAUSALITY_NOT_IN_EVIDENCE", "ENTITY_NOT_IN_EVIDENCE", "UNIT_MISMATCH",
                 "RELATIVE_CHANGE_UNSUPPORTED", "ACCUSATION_NOT_IN_EVIDENCE", "NON_LATIN_SCRIPT",
                 "QUALIFIER_DATE_UNSUPPORTED"}
    for e in events.values():
        pkg = build_template_package(e)
        assert not {i.code for i in pkg.validation.issues} & new_codes, (e.event_id, pkg.validation.issues)


def test_fixture_cached_packages_still_validate(events, bundle):
    for p in bundle.packages:
        cleaned, _ = validate_package(p, events[p.event_id])
        assert len(cleaned.brief) == len(p.brief), cleaned.validation.issues


def test_internal_claim_ids_are_not_unsupported_entities():
    from scayl.gen.validators import _unsupported_names
    text = "Según telemetro.com, hubo un sismo de magnitud 4.7. (claim_ids: CLM-0125-002, CLM-0125-004)"
    assert _unsupported_names(text, "sismo de magnitud 4.7 sacude la frontera") == []
