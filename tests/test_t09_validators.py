"""T09 (validator half): citations valid, facts vs statements distinguished, no invented numbers."""
from scayl.contracts import ClaimType, TaggedSentence
from scayl.gen.template import build_template_package
from scayl.gen.validators import SCOPE_PHRASE, _Ctx, check_sentence, numbers_in, validate_package


def _ctx(event):
    return _Ctx(claims={c.claim_id: c for c in event.claims})


def S(text, tag=ClaimType.HECHO, ids=()):
    return TaggedSentence(text=text, tag=tag, claim_ids=list(ids))


def test_number_parsing_accepts_both_decimal_conventions():
    assert 4.6 in numbers_in("magnitud 4,6") and 4.6 in numbers_in("magnitud 4.6")
    assert not numbers_in("ver CLM-0001-001")


def test_supported_fact_passes(events):
    e = events["EVT-0001"]
    assert check_sentence(S("USGS registró un sismo de magnitud 4.6.", ids=["CLM-0001-001"]), _ctx(e), "t")


def test_invented_number_is_removed(events):
    ctx = _ctx(events["EVT-0001"])
    assert check_sentence(S("El sismo fue de magnitud 5.2.", ids=["CLM-0001-001"]), ctx, "t") is None
    assert ctx.issues[0].code == "NUMBER_NOT_IN_EVIDENCE"


def test_uncited_fact_is_removed(events):
    ctx = _ctx(events["EVT-0001"])
    assert check_sentence(S("Hubo heridos en Chiriquí."), ctx, "t") is None
    assert ctx.issues[0].code == "UNCITED_FACT"


def test_unknown_claim_id_is_removed(events):
    ctx = _ctx(events["EVT-0001"])
    assert check_sentence(S("Algo.", ids=["CLM-9999-001"]), ctx, "t") is None


def test_reported_claim_as_fact_without_attribution_is_removed(events):
    """The 'interpretive overconfidence' failure (arXiv 2509.25498)."""
    ctx = _ctx(events["EVT-0003"])
    out = check_sentence(S("Las esclusas cerrarán la próxima semana.", ids=["CLM-0003-001"]), ctx, "t")
    assert out is None and ctx.issues[0].code == "STATUS_MISMATCH"
    assert ctx.attribution.candidates == 1 and ctx.attribution.preserved_before == 0


def test_reported_claim_with_attribution_is_retagged_as_statement(events):
    ctx = _ctx(events["EVT-0003"])
    out = check_sentence(S("Según un medio, las esclusas cerrarán la próxima semana.", ids=["CLM-0003-001"]),
                         ctx, "t")
    assert out is not None and out.tag == ClaimType.DECLARACION


def test_absence_of_evidence_can_be_stated(events):
    e = events["EVT-0001"]
    assert check_sentence(S("No hay datos verificados de daños.", ids=["CLM-0001-002"]), _ctx(e), "t")


def test_invented_quotes_and_interviews_are_removed(events):
    ctx = _ctx(events["EVT-0001"])
    assert check_sentence(S('Un vecino dijo "se movió toda la casa" tras el sismo de 4.6.',
                            ids=["CLM-0001-001"]), ctx, "t") is None
    assert check_sentence(S("En entrevista, el director confirmó el sismo de 4.6.", ids=["CLM-0001-001"]),
                          ctx, "t") is None


def test_template_package_is_valid_and_carries_scope_phrase(events):
    for e in events.values():
        pkg = build_template_package(e)
        assert pkg.generated_by.mode == "template"
        assert len(pkg.investigation_questions) == 3
        if e.claims:
            assert pkg.validation.passed, pkg.validation.issues
        assert pkg.scope_disclaimer == SCOPE_PHRASE
        assert len(" ".join(s.text for s in pkg.brief).split()) <= 250
        # every surviving fact cites a claim of the event
        ids = {c.claim_id for c in e.claims}
        assert all(set(s.claim_ids) <= ids and s.claim_ids for s in pkg.brief)


def test_validate_package_reports_and_cleans(events, bundle):
    e = events["EVT-0001"]
    pkg = bundle.packages[0].model_copy(update={"brief": [
        S("USGS registró un sismo de magnitud 4.6.", ids=["CLM-0001-001"]),
        S("Murieron 12 personas.", ids=["CLM-0001-001"]),
    ]})
    cleaned, _ = validate_package(pkg, e)
    assert [s.text for s in cleaned.brief] == ["USGS registró un sismo de magnitud 4.6."]
    assert any(i.code == "NUMBER_NOT_IN_EVIDENCE" for i in cleaned.validation.issues)
    assert cleaned.validation.passed


def test_date_parts_only_support_numbers_used_as_dates(events):
    """Regression: '12' from the evidence timestamp 2025-09-12 must not support '12 personas'."""
    e = events["EVT-0001"]
    assert check_sentence(S("Murieron 12 personas.", ids=["CLM-0001-001"]), _ctx(e), "t") is None
    assert check_sentence(S("El 12 de septiembre de 2025 USGS registró magnitud 4.6.", ids=["CLM-0001-001"]),
                          _ctx(e), "t")


def test_absence_phrasings_are_recognised(events):
    e = events["EVT-0001"]
    for text in ["Sin reportes verificados de daños.", "No se reportan daños en el corpus.",
                 "Sin información confirmada sobre daños."]:
        assert check_sentence(S(text, ids=["CLM-0001-002"]), _ctx(e), "t"), text
