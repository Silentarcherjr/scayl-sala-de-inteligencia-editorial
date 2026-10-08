"""Regressions for the 5 non-"sí" rows of the human support review (data/labels/support_review.csv).

All five were template sentences "Según <medio>: <titular>." whose only evidence was that same headline.
Each test rebuilds the failure pattern on SYNTHETIC headlines (never the reviewed rows, which stay
immutable) and checks the generalizable fix in template + validators. Before the fix every reported
headline was emitted bare: no date, no status, no language label, no judicial caveat, any script.
"""
from datetime import UTC, datetime

from scayl.contracts import ClaimStatus, ClaimType, TaggedSentence, Topic
from scayl.evidence.assemble import build_event
from scayl.gen.template import build_template_package, headline_language
from scayl.gen.validators import _Ctx, _non_latin, check_sentence, validate_package
from tests.factories import CUTOFF, news

DET = datetime(2025, 8, 28, 15, tzinfo=UTC)


def _event(titulo, medio="medio-a.com", pub=None, det=DET, eid="EVT-0901"):
    item = news("x1", titulo, medio=medio, pub=pub, det=det)
    return build_event(eid, [item], Topic.LOGISTICA_CANAL, 0.9, [], [], CUTOFF)


def _reported(pkg, event):
    cid = next(c.claim_id for c in event.claims if c.status == ClaimStatus.SOLO_REPORTADA)
    return next(s for s in pkg.brief if s.claim_ids == [cid])


def test_sr04_undated_present_tense_headline_carries_its_date_and_status():
    """SR04 (parcial): 'cruza el Canal' in present tense, no publication date, a month old."""
    e = _event("El buque gasífero del ejemplo cruza el Canal de Panamá")
    pkg = build_template_package(e)
    s = _reported(pkg, e)
    assert "evento detectado: 2025-08-28" in s.text
    assert "sin confirmación oficial en el corpus" in s.text
    assert s.tag == ClaimType.DECLARACION and pkg.validation.passed


def test_sr04_qualifier_date_must_come_from_event_metadata():
    """An LLM (or a bug) cannot forge the metadata qualifier with another date."""
    e = _event("El buque del ejemplo cruza el Canal de Panamá")
    cid = e.claims[0].claim_id
    forged = TaggedSentence(text="Según medio-a.com (evento detectado: 2026-10-07; sin confirmación oficial en el "
                                 "corpus): El buque del ejemplo cruza el Canal de Panamá.",
                            tag=ClaimType.DECLARACION, claim_ids=[cid])
    pkg = build_template_package(e).model_copy(update={"brief": [forged]})
    cleaned, _ = validate_package(pkg, e)
    assert not cleaned.brief
    assert any(i.code == "QUALIFIER_DATE_UNSUPPORTED" for i in cleaned.validation.issues)


def test_sr05_non_latin_headline_is_not_reproduced_untranslated():
    """SR05 (no): English + Marathi headline pasted into a Spanish brief."""
    e = _event("Canal Water Shortage Impact ; पाणी जगाला रडवणार! जलमार्ग संकटात", medio="ejemplo-mr.com")
    pkg = build_template_package(e)
    s = _reported(pkg, e)
    assert not _non_latin(s.text) and "no se reproduce sin traducción verificada" in s.text
    assert any(p.startswith("Traducir y verificar el titular original de ejemplo-mr.com") and "news:x1" in p
               for p in pkg.pending_verifications)
    assert all(not _non_latin(x.text) for x in pkg.brief + pkg.script + [pkg.social_copy])
    assert pkg.validation.passed


def test_sr05_validator_removes_non_latin_sentences_in_any_mode():
    e = _event("Canal Water Shortage Impact ; पाणी जगाला रडवणार", medio="ejemplo-mr.com")
    llm_sentence = TaggedSentence(text="Según ejemplo-mr.com, पाणी जगाला रडवणार.", tag=ClaimType.DECLARACION,
                                  claim_ids=[e.claims[0].claim_id])
    pkg = build_template_package(e)
    cleaned, _ = validate_package(pkg.model_copy(update={"brief": [llm_sentence, *pkg.brief]}), e)
    assert llm_sentence.text not in [s.text for s in cleaned.brief]
    assert any(i.code == "NON_LATIN_SCRIPT" for i in cleaned.validation.issues)


def test_sr10_single_outlet_claim_reads_as_unconfirmed_attribution():
    """SR10 (no): a single outlet's 'primera mujer que asume' read as an established fact."""
    e = _event("Cambio de liderazgo en la entidad del ejemplo: Ana Pérez, primera mujer que asume la dirección")
    s = _reported(build_template_package(e), e)
    assert s.text.startswith("Según medio-a.com (") and "sin confirmación oficial en el corpus" in s.text
    # The same content as an unattributed fact is still removed (pre-existing rule, kept).
    ctx = _Ctx(claims={c.claim_id: c for c in e.claims})
    bare = TaggedSentence(text="Ana Pérez es la primera mujer que asume la dirección.", tag=ClaimType.HECHO,
                          claim_ids=[e.claims[0].claim_id])
    assert check_sentence(bare, ctx, "t") is None and ctx.issues[0].code == "STATUS_MISMATCH"


def test_sr19_judicial_headline_gets_responsibility_caveat():
    """SR19 (no): reported prosecution measures read as established wrongdoing."""
    e = _event("Fiscalía amplía medidas cautelares en caso Ejemplo e incluye nueva empresa vinculada a Panamá")
    s = _reported(build_template_package(e), e)
    assert "asunto judicial: lo atribuido no establece responsabilidad" in s.text


def test_sr19_accusation_absent_from_evidence_is_removed():
    e = _event("Fiscalía amplía medidas cautelares en caso Ejemplo e incluye nueva empresa vinculada a Panamá")
    ctx = _Ctx(claims={c.claim_id: c for c in e.claims})
    s = TaggedSentence(text="Según medio-a.com, la nueva empresa es culpable de fraude en el caso Ejemplo.",
                       tag=ClaimType.DECLARACION, claim_ids=[e.claims[0].claim_id])
    assert check_sentence(s, ctx, "t") is None and ctx.issues[0].code == "ACCUSATION_NOT_IN_EVIDENCE"


def test_sr25_foreign_latin_headline_is_labelled_not_passed_as_spanish():
    """SR25 (parcial): Portuguese headline quoted as if it were Spanish copy."""
    e = _event("Seca pelo El Niño pode levar Canal do Panamá a novas restrições", medio="ejemplo.com.br")
    pkg = build_template_package(e)
    s = _reported(pkg, e)
    assert "titular original en portugués, sin traducir" in s.text and pkg.validation.passed
    assert any("Traducir y verificar" in p for p in pkg.pending_verifications)


def test_language_detection_does_not_flag_spanish_headlines():
    """False-positive guard on real-looking Spanish headlines (incl. 'El Niño', 'do' in domains)."""
    for t in ["Canal de Panamá aplica nueva reducción del calado para enfrentar el fenómeno de El Niño",
              "Canal de Panamá aumentará a 33 los cupos diarios de tránsito",
              "Sismo en Panamá hoy: IGUP descarta que hoy lunes 31 de agosto no se ha registrado algún temblor",
              "Mulino visitará Ecuador el viernes para hablar sobre economía y seguridad"]:
        assert headline_language(t) is None, t
    assert headline_language("El Niño fait baisser le niveau du canal de Panama et perturbe le commerce") == "fr"
    assert headline_language("Panama Canal water shortage and the impact on shipping for India") == "en"
