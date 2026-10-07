import pytest

from scayl.eval.human_labels import confirmed


def test_proposals_are_not_human_gold():
    rows = [{"id_noticia": "a", "tema_propuesto": "economia", "tema_humano": "null", "confirmado": "null", "revisor": "null"}]
    assert confirmed(rows, "tema_humano") == []
    with pytest.raises(ValueError, match="label and reviewer"):
        confirmed([{**rows[0], "confirmado": "si"}], "tema_humano")


def test_explicit_review_requires_unique_ids():
    row = {"id_noticia": "a", "tema_humano": "turismo", "confirmado": "si", "revisor": "humano"}
    assert confirmed([row], "tema_humano") == [row]
    with pytest.raises(ValueError, match="Duplicate"):
        confirmed([row, row], "tema_humano")
