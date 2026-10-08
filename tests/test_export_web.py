"""Public export parity, privacy, nulls and reproducibility."""
import json
from pathlib import Path

import pytest

from deploy.prepare import check_public
from scayl.contracts import UIBundle
from scripts.export_web import ROOT, export


def test_export_public_parity(tmp_path):
    export(tmp_path)
    bundle = UIBundle.model_validate_json((ROOT / "deploy/artifacts/v1/bundle.public.json").read_text())
    expected = sorted(bundle.events, key=lambda e: (-e.priority.score, -e.priority.components.U, e.event_id))
    rows = json.loads((tmp_path / "events.json").read_text())
    assert [r["event_id"] for r in rows] == [e.event_id for e in expected]
    assert len(rows) == len(bundle.events)
    for event in expected:
        case = json.loads((tmp_path / f"cases/{event.event_id}.json").read_text())
        assert {k: case[k] for k in event.model_dump()} == event.model_dump(mode="json")
        package = next((p for p in bundle.packages if p.event_id == event.event_id), None)
        assert case["package"] == (package.model_dump(mode="json") if package else None)
        assert all("descripcion" not in h for h in case["headlines"])
    first = {}
    for path in tmp_path.rglob("*.json"):
        value = json.loads(path.read_text())
        check_public(value)
        if path.name == "meta.json":
            value.pop("exported_at")
        first[path.relative_to(tmp_path)] = value
    export(tmp_path)
    for relative, value in first.items():
        second = json.loads((tmp_path / relative).read_text())
        if relative == Path("meta.json"):
            second.pop("exported_at")
        assert second == value
    assert rows[0]["event_id"] == "EVT-0101"
    assert rows[0]["last_published"] is None
    qa = first[Path("qa.json")]
    assert len(qa["examples"]) == 4 and len(qa["jury"]) == 4
    assert qa["jury"][2]["answer"]["abstained"]


def test_export_rejects_rss_description(tmp_path, monkeypatch):
    from scayl import service

    bundle = UIBundle.model_validate_json((ROOT / "deploy/artifacts/v1/bundle.public.json").read_text())
    bundle.news[0].descripcion = "contenido no público"
    monkeypatch.setattr(service, "reload", lambda: None)
    monkeypatch.setattr(service, "load_bundle", lambda: bundle)
    with pytest.raises(ValueError, match="descripción RSS"):
        export(tmp_path)
    assert not list(tmp_path.rglob("*.json"))
