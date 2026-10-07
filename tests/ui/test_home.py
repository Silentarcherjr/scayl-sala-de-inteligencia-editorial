from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from scayl import service

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def home(bundle, monkeypatch):
    monkeypatch.setattr(service, "load_bundle", lambda: bundle)
    return AppTest.from_file(str(ROOT / "app/Home.py"), default_timeout=15)


def test_rank_funnel_matrix_and_editorial_safeguards(home):
    home.run()
    assert not home.exception
    assert [m.value for m in home.metric] == ["6", "6", "3", "3"]
    rows = home.dataframe[0].value
    assert list(rows["Caso"]) == ["EVT-0003", "EVT-0001", "EVT-0002"]
    assert rows.iloc[0]["Evidencia"] == "insuficiente"
    assert "NO habilita publicación" in rows.iloc[0]["Acción"]
    assert rows.iloc[0]["Publicación (Panamá)"] == "2025-09-29 17:00"
    matrix = home.dataframe[1].value.set_index("Rango")
    assert matrix.loc["alto", "insuficiente"] == 1
    assert matrix.loc["alto", "suficiente_para_borrador"] == 1
    assert matrix.loc["medio", "parcial"] == 1
    assert matrix.to_numpy().sum() == 3
    assert len(home.get("progress")) == 15
    assert len(home.get("page_link")) == 6


def test_ties_use_urgency_then_id(home, bundle):
    for event in bundle.events:
        event.priority.score = 70
        event.priority.components.U = 0.5
    bundle.events[1].priority.components.U = 0.9
    bundle.events.reverse()
    home.run()
    assert not home.exception
    assert list(home.dataframe[0].value["Caso"]) == ["EVT-0002", "EVT-0001", "EVT-0003"]


def test_filters_and_empty_intersection(home):
    home.run()
    home.selectbox[0].select("economia").run()
    assert list(home.dataframe[0].value["Caso"]) == ["EVT-0002"]
    assert home.dataframe[1].value.drop(columns="Rango").to_numpy().sum() == 1
    home.selectbox[1].select("insuficiente").run()
    assert not home.exception
    assert any("No hay eventos" in item.value for item in home.info)
    assert home.dataframe[0].value.drop(columns="Rango").to_numpy().sum() == 0


def test_empty_snapshot_and_null_dates(home, bundle):
    bundle.events[0].last_published = None
    bundle.events[0].first_detected = None
    home.run()
    row = home.dataframe[0].value.set_index("Caso").loc["EVT-0001"]
    assert row["Publicación (Panamá)"] == "no disponible"
    assert row["Detección (Panamá)"] == "no disponible"
    bundle.events = []
    home.run()
    assert not home.exception
    assert home.metric[2].value == "0"


def test_consultas_placeholder_is_explicit():
    page = AppTest.from_file(str(ROOT / "app/pages/2_Consultas.py")).run()
    assert not page.exception
    assert "preparación" in page.info[0].value
