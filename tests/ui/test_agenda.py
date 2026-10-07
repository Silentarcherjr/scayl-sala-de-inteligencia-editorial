from pathlib import Path

from streamlit.testing.v1 import AppTest

from app.components.agenda import top_reasons
from scayl import service


def test_reasons_use_weighted_contribution_not_raw_component(bundle):
    event = bundle.events[0]
    event.priority.components.R = 0.6
    event.priority.components.I = 0.7
    event.priority.components.U = 0.1
    event.priority.components.N = 0.1
    event.priority.components.E = 1.0
    reasons = top_reasons(event, {"R": 30, "I": 25, "U": 20, "N": 15, "E": 10})
    assert [key for key, _ in reasons] == ["R", "I"]
    assert reasons[0][1] == event.priority.components.rationale["R"]


def test_agenda_has_five_cards_stable_order_and_survives_filters(bundle, monkeypatch):
    extra = [bundle.events[0].model_copy(deep=True) for _ in range(4)]
    for n, event in enumerate(extra):
        event.event_id = f"EVT-10{n:02}"
    bundle.events.extend(extra)
    monkeypatch.setattr(service, "load_bundle", lambda: bundle)
    page = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "app/Home.py")).run()
    assert not page.exception
    links = [x.label for x in page.get("page_link") if x.label.startswith("Investigar")]
    assert links == ["Investigar EVT-0003", "Investigar EVT-0001", "Investigar EVT-1000",
                     "Investigar EVT-1001", "Investigar EVT-1002"]
    assert any("no evidencia" in x.value for x in page.caption)
    page.selectbox[0].select("economia").run()
    assert [x.label for x in page.get("page_link") if x.label.startswith("Investigar")] == links
