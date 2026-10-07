import csv
import json

import pytest

from scayl.ingest.common import write_once, write_csv
from scayl.ingest import common
from urllib.error import HTTPError
from scayl.ingest.fetch_gdelt import article_row, normalize_url
from scayl.ingest.fetch_worldbank import complete_grid, INDICATORS
from scayl.ingest.manifest import build_manifest, verify_manifest
from scayl.ingest.editor_candidates import export
from scayl.ingest.fetch_gkg import extract
from scayl.ingest import fetch_usgs, fetch_worldbank
from scayl.ingest.fetch_tvn import historical_rows
from datetime import datetime, timezone
import io
import zipfile
import hashlib
import shutil
from pathlib import Path
import yaml


def test_immutable_bytes(tmp_path):
    path = tmp_path / "raw.json"
    write_once(path, b"original")
    write_once(path, b"original")
    with pytest.raises(FileExistsError):
        write_once(path, b"modified")
    assert path.read_bytes() == b"original"


def test_worldbank_grid_preserves_null_and_zero():
    records = [{"countryiso3code": "PAN", "date": "2024", "value": 0,
                "indicator": {"value": "Population"}}]
    rows = complete_grid(records, "SP.POP.TOTL", "2026-10-06T00:00:00Z", "https://example.test")
    assert len(rows) == 90
    assert len(INDICATORS) * len(rows) == 540
    assert next(row for row in rows if row["pais_iso3"] == "PAN" and row["anio"] == 2024)["valor"] == 0
    assert sum(row["valor"] is None for row in rows) == 89


def test_csv_has_explicit_null_not_empty_string(tmp_path):
    path = tmp_path / "nulls.csv"
    write_csv(path, [{"valor": None}, {"valor": 0}], ["valor"])
    assert path.read_text() == "valor\nnull\n0\n"


def test_gdelt_detection_is_not_publication():
    article = {"url": "https://WWW.TVN-2.COM/noticia#fragment", "title": "Titular",
               "seendate": "20250901T120000Z", "language": "Spanish"}
    row = article_row(article, "2026-10-06T00:00:00Z")
    assert row["fecha_publicacion"] is None
    assert row["fecha_deteccion"] == "2025-09-01T12:00:00Z"
    assert row["origen"] == "gdelt" and row["medio"] == "TVN"
    assert row["url"] == "https://www.tvn-2.com/noticia"
    assert article_row({**article, "url": row["url"]}, "another extraction")["id_noticia"] == row["id_noticia"]
    with pytest.raises(ValueError):
        normalize_url("javascript:alert(1)")


def make_snapshot(path):
    write_csv(path / "noticias.csv", [{"id_noticia": "one", "titulo": "Titular", "medio": "TVN",
              "fecha_publicacion": None, "fecha_deteccion": "2025-09-01T00:00:00Z"}],
              ["id_noticia", "titulo", "medio", "fecha_publicacion", "fecha_deteccion"])
    write_once(path / "indicadores.csv", b"valor\nnull\n")
    write_once(path / "eventos.geojson", b'{"type":"FeatureCollection","features":[]}')
    write_once(path / "fuentes.json", b"[]")


def test_manifest_detects_one_byte_missing_and_extra(tmp_path):
    make_snapshot(tmp_path)
    manifest = build_manifest(tmp_path)
    assert manifest["archivos"]["indicadores.csv"]["cantidad"] == 1
    assert verify_manifest(tmp_path) == []
    assert build_manifest(tmp_path) == manifest
    (tmp_path / "indicadores.csv").write_bytes(b"valor\nNull\n")
    assert verify_manifest(tmp_path) == ["changed:indicadores.csv"]
    with pytest.raises(ValueError, match="Frozen snapshot"):
        build_manifest(tmp_path)
    (tmp_path / "fuentes.json").unlink()
    (tmp_path / "extra.txt").write_text("extra")
    assert set(verify_manifest(tmp_path)) == {"changed:indicadores.csv", "missing:fuentes.json", "unexpected:extra.txt"}


def test_manifest_refuses_incomplete_snapshot(tmp_path):
    with pytest.raises(ValueError, match="Incomplete"):
        build_manifest(tmp_path)


def test_manifest_is_portable_without_local_responses(tmp_path):
    source = tmp_path / "source"
    make_snapshot(source)
    local = {"responses/gkg/sample.gkg.csv.zip": b"local GKG bytes",
             "responses/tvn-current/rss.xml": b"<rss><description>local</description></rss>"}
    for name, data in local.items():
        write_once(source / name, data)
    manifest = build_manifest(source)
    window = yaml.safe_load(Path("scayl/config/data_window.v1.yaml").read_text(encoding="utf-8"))
    assert manifest["fecha_corte_UTC"] == window["cutoff_utc"]
    assert not set(local) & manifest["archivos"].keys()
    inventory = json.loads((source / "acquisition_inventory.json").read_text())
    for name, data in local.items():
        assert inventory["files"][name]["sha256"] == hashlib.sha256(data).hexdigest()
        assert inventory["files"][name]["disponibilidad"] == "solo local"
        assert (source / name).read_bytes() == data
    clone = tmp_path / "clone"
    for name in [*manifest["archivos"], "manifest.json"]:
        (clone / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, clone / name)
    assert verify_manifest(clone) == []
    assert build_manifest(clone) == manifest
    assert verify_manifest(source) == []
    (clone / "acquisition_inventory.json").write_text("{}")
    assert verify_manifest(clone) == ["changed:acquisition_inventory.json"]


def test_manifest_refuses_inconsistent_local_hashes(tmp_path):
    make_snapshot(tmp_path)
    write_once(tmp_path / "responses/gkg/sample.zip", b"local")
    write_once(tmp_path / "acquisition_inventory.json", b'{"files":{}}')
    with pytest.raises(ValueError, match="Local acquisition inventory mismatch"):
        build_manifest(tmp_path)
    assert not (tmp_path / "manifest.json").exists()


def test_editor_handoff_has_no_scores_and_keeps_dates(tmp_path):
    make_snapshot(tmp_path)
    output = tmp_path / "editor.csv"
    export(tmp_path, output)
    with output.open() as handle:
        rows = list(csv.DictReader(handle))
    assert set(rows[0]) == {"id_noticia", "titulo", "medio", "fecha_publicacion", "fecha_deteccion"}
    assert rows[0]["fecha_publicacion"] == "null"
    with pytest.raises(FileExistsError):
        export(tmp_path, output)


def test_gkg_invalid_encoding_is_excluded_with_reason():
    fields = [""] * 27
    fields[1] = "20250901180000"
    fields[3] = "tvn-2.com"
    fields[4] = "https://www.tvn-2.com/noticia"
    fields[25] = "srclc:spa;"
    fields[26] = "<PAGE_TITLE>Panam&#xE1;: Canal</PAGE_TITLE>"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("data.csv", b"invalid\xbb\n" + "\t".join(fields).encode() + b"\nshort\trow\n")
    excluded = []
    rows = extract(buffer.getvalue(), "2026-10-06T00:00:00Z", excluded)
    assert len(rows) == 1
    assert rows[0]["titulo"] == "Panamá: Canal"
    assert rows[0]["idioma"] == "spa"
    assert rows[0]["fecha_publicacion"] is None
    assert excluded == [{"member": "data.csv", "line": 1, "reason": "invalid_utf8"},
                        {"member": "data.csv", "line": 3, "reason": "fewer_than_27_fields"}]


def test_usgs_pagination_and_exclusive_end(tmp_path, monkeypatch):
    calls = []
    def fake_download(directory, name, url, params):
        calls.append(params["offset"])
        features = ([{"id": "in", "properties": {"time": 1735689599999}},
                     {"id": "out", "properties": {"time": 1735689600000}}]
                    if params["offset"] == 1 else [])
        return json.dumps({"type": "FeatureCollection", "features": features}).encode(), {}
    monkeypatch.setitem(fetch_usgs.PARAMS, "limit", 2)
    monkeypatch.setattr(fetch_usgs, "download", fake_download)
    result = fetch_usgs.fetch(tmp_path)
    assert calls == [1, 3]
    assert [feature["id"] for feature in result["features"]] == ["in"]


def test_worldbank_pagination(tmp_path, monkeypatch):
    calls = []
    def fake_download(directory, name, url, params):
        calls.append((url, params["page"]))
        indicator = url.rsplit("/", 1)[-1]
        records = [{"countryiso3code": "PAN", "date": str(2025 - params["page"]),
                    "value": None if params["page"] == 1 else 0,
                    "indicator": {"value": indicator}}]
        return json.dumps([{"pages": 2}, records]).encode(), {"fecha_extraccion": "2026-10-06T00:00:00Z"}
    monkeypatch.setattr(fetch_worldbank, "download", fake_download)
    rows = fetch_worldbank.fetch(tmp_path)
    assert len(calls) == 12 and len(rows) == 540
    assert sum(row["valor"] == 0 for row in rows) == 6
    assert sum(row["valor"] is None for row in rows) == 534


def test_rss_historical_adapter_preserves_publication_and_excludes_cutoff():
    items = [{"titulo": "[SINTÉTICO] Titular", "url": f"https://www.tvn-2.com/{index}",
              "fecha_publicacion_original": published, "fecha_extraccion": "2026-10-06T21:00:00Z"}
             for index, published in enumerate(["Mon, 01 Sep 2025 07:00:00 -0500",
                                                "Wed, 01 Oct 2025 00:00:00 +0000",
                                                "Tue, 06 Oct 2026 12:00:00 +0000"])]
    rows = historical_rows(items + [items[0]], datetime(2024, 1, 1, tzinfo=timezone.utc),
                           datetime(2025, 10, 1, tzinfo=timezone.utc))
    assert len(rows) == 1
    assert rows[0]["fecha_publicacion"] == "2025-09-01T12:00:00Z"
    assert rows[0]["fecha_deteccion"] == "2026-10-06T21:00:00Z"
    assert rows[0]["origen"] == "tvn_rss"


def test_download_caches_bytes_and_rejects_changed_request(tmp_path, monkeypatch):
    class Response:
        status = 200
        headers = {"Content-Type": "application/json"}
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def read(self):
            return b'{"value":null}'
    calls = []
    def opener(request, timeout):
        calls.append(request.full_url)
        return Response()
    monkeypatch.setattr(common, "urlopen", opener)
    first = common.download(tmp_path, "source.json", "https://example.test", {"page": 1})
    assert common.download(tmp_path, "source.json", "https://example.test", {"page": 1}) == first
    assert len(calls) == 1
    with pytest.raises(ValueError, match="mismatch"):
        common.download(tmp_path, "source.json", "https://example.test", {"page": 2})
    (tmp_path / "source.json").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="mismatch"):
        common.download(tmp_path, "source.json", "https://example.test", {"page": 1})


def test_download_bounds_retries_and_records_failure(tmp_path, monkeypatch):
    pauses = []
    def opener(request, timeout):
        raise HTTPError(request.full_url, 429, "rate limited", {"Retry-After": "6"}, None)
    monkeypatch.setattr(common, "urlopen", opener)
    monkeypatch.setattr(common.time, "sleep", pauses.append)
    with pytest.raises(HTTPError):
        common.download(tmp_path, "source.json", "https://example.test")
    assert pauses == [6, 6]
    failure = json.loads(next((tmp_path / "failures").glob("*.json")).read_text())
    assert len(failure["attempts"]) == 3
    assert not (tmp_path / "source.json").exists()
