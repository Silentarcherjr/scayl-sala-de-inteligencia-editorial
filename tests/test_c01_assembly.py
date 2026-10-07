"""Acquisition boundary tests with synthetic metadata only."""
import json
from datetime import timedelta

from scayl.ingest.assemble_c01 import collect
from scayl.ingest.common import json_bytes, write_once
from scayl.ingest.window import news_window


def test_c01_rss_wins_duplicate_and_old_raw_is_audited(tmp_path):
    start, end = news_window()
    published = end - timedelta(days=2)
    rss = {"titulo": "[SINTÉTICO] Titular", "url": "https://www.tvn-2.com/test",
           "fecha_publicacion_original": published.strftime("%a, %d %b %Y %H:%M:%S +0000"),
           "fecha_extraccion": end.isoformat()}
    write_once(tmp_path / "tvn_rss_actual.json", json_bytes({"items": [rss]}))
    for label, date in [("current", published), ("old", start - timedelta(days=1))]:
        path = tmp_path / f"responses/gdelt/{label}.json"
        write_once(path, json_bytes({"articles": [{"url": rss["url"], "title": rss["titulo"],
                   "seendate": date.strftime("%Y%m%dT%H%M%SZ")}]}))
        write_once(path.with_name(path.name + ".request.json"), json_bytes({"fecha_extraccion": end.isoformat()}))
    old_zip = tmp_path / "responses/gkg/20250901180000.translation.gkg.csv.zip"
    write_once(old_zip, b"do not parse out-of-window raw")
    rows, audit = collect(tmp_path)
    assert len(rows) == 1
    assert rows[0]["origen"] == "tvn_rss"
    assert rows[0]["fecha_deteccion"] is None
    assert rows[0]["fecha_publicacion"] == published.isoformat().replace("+00:00", "Z")
    assert {entry["reason"] for entry in audit["excluded"]} == {"duplicado_url", "fuera_de_ventana_C-01"}
    assert old_zip.read_bytes() == b"do not parse out-of-window raw"


def test_doc_circuit_breaker_records_incomplete_plan(tmp_path, monkeypatch):
    from scayl.ingest import acquire_c01
    def fail(*args, **kwargs):
        raise OSError("rate limited")
    monkeypatch.setattr(acquire_c01, "download", fail)
    monkeypatch.setattr(acquire_c01.time, "sleep", lambda _: None)
    report = acquire_c01.acquire(tmp_path)
    assert len(report["attempts"]) == 3
    assert report["complete"] is False
    assert report["stopped_after_consecutive_failures"] is True
    assert json.loads(next(tmp_path.glob("doc-c01-*.json")).read_bytes()) == report
    assert not (tmp_path / "noticias.csv").exists()
