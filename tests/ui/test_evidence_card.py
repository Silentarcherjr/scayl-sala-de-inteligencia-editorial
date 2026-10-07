from streamlit.testing.v1 import AppTest


def render_card(value, period, url):
    from app.components.evidence_card import evidence_card
    from scayl.contracts import EvidenceKind, EvidenceRef

    evidence_card(EvidenceRef(evidence_id="wb:PAN:test:2024", kind=EvidenceKind.INDICATOR,
                              field="valor", value=value, period=period, url=url))


def test_null_is_preserved_and_historical_period_is_warned():
    page = AppTest.from_function(render_card, args=(None, "2024", "https://example.invalid")).run()
    assert not page.exception
    assert "no disponible (nulo)" in page.expander[0].label
    assert "Dato histórico — 2024" in page.warning[0].value
    assert any(item.value == "Extracto: no disponible" for item in page.text)


def test_zero_is_visible_without_inventing_period_or_link():
    page = AppTest.from_function(render_card, args=(0, None, None)).run()
    assert not page.exception
    assert page.expander[0].label.startswith("0 ·")
    assert any(item.value == "Período: no disponible" for item in page.text)
    assert any(item.value == "URL: no disponible" for item in page.text)
    assert not page.warning
