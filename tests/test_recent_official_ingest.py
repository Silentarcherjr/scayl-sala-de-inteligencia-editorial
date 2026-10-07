from datetime import UTC, date, datetime

import pytest

from scayl.ingest.recent_official import acp_history, acp_projections, daily_rows, inec_transcription


def test_history_cutoff_and_missing_values():
    raw = b"DATE_LOG,GATUN_LAKE_LEVEL(FEET)\r\r\n2026-09-29,84.88\r\r\n2026-09-30,\r\r\n2026-10-01,85.03\r\r\n"
    start, end = date(2026, 9, 29), date(2026, 10, 1)
    values = acp_history(raw, start, end)
    assert values == {"2026-09-29": 84.88, "2026-09-30": None}
    rows = daily_rows(values, start, end, series="ACP.GATUN.NIVEL", name="observado",
                      receipt={"url": "https://example.com", "fecha_extraccion": "2026-10-07T00:00:00Z"},
                      projection=False)
    assert rows[1]["valor"] is None
    assert all(r["es_proyeccion"] == "false" for r in rows)


def test_projection_requires_pre_cutoff_issue_date():
    raw = b"Disclaimer\r\nprojected_date,projected_gatun_water_level\r\n09/30/2026, 85.2\r\n10/01/2026, 85.3\r\n"
    cutoff = datetime(2026, 10, 1, tzinfo=UTC)
    args = (raw, date(2026, 9, 30), date(2026, 10, 1))
    assert acp_projections(*args, published_at=None, cutoff=cutoff) == {}
    assert acp_projections(*args, published_at=cutoff, cutoff=cutoff) == {}
    assert acp_projections(*args, published_at=datetime(2026, 9, 29, tzinfo=UTC), cutoff=cutoff) == {"2026-09-30": 85.2}


def test_transcription_rejects_wrong_pdf_and_future_publication():
    import hashlib
    pdf = b"fixture"
    transcription = {"pdf_sha256": hashlib.sha256(pdf).hexdigest(),
                     "published_at": "2026-09-14T00:00:00Z",
                     "rows": [{"periodo": "2026-08", "mensual": -0.3, "interanual": None}]}
    receipt = {"url": "https://example.com/ipc.pdf", "fecha_extraccion": "2026-10-07T00:00:00Z"}
    cutoff = datetime(2026, 10, 1, tzinfo=UTC)
    rows = inec_transcription(pdf, transcription, receipt, cutoff)
    assert rows[0]["valor"] == -0.3
    assert rows[1]["valor"] is None
    with pytest.raises(ValueError, match="different PDF"):
        inec_transcription(b"changed", transcription, receipt, cutoff)
    with pytest.raises(ValueError, match="after the cutoff"):
        inec_transcription(pdf, {**transcription, "published_at": "2026-10-01T00:00:00Z"}, receipt, cutoff)


def test_declared_addition_archives_parent_and_rejects_mutation(tmp_path):
    import hashlib
    import json
    from scayl.ingest.manifest import _inventory, declare_addition, verify_manifest
    raw = tmp_path / "noticias.csv"
    raw.write_text("id_noticia,titulo\na,Headline\n", encoding="utf-8")
    parent = {"archivos": _inventory(tmp_path), "fuentes": [], "transformaciones": [],
              "fecha_corte_UTC": "2026-10-01T00:00:00Z"}
    original = json.dumps(parent).encode()
    (tmp_path / "manifest.json").write_bytes(original)
    digest = hashlib.sha256(original).hexdigest()
    (tmp_path / "indicadores_recientes.csv").write_text("periodo,valor\n2026-08,-0.3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="fingerprint"):
        declare_addition(tmp_path, parent_sha256="wrong", version="v1.1")
    raw.write_text("modified", encoding="utf-8")
    with pytest.raises(ValueError, match="Existing raw changed"):
        declare_addition(tmp_path, parent_sha256=digest, version="v1.1")
    raw.write_text("id_noticia,titulo\na,Headline\n", encoding="utf-8")
    updated = declare_addition(tmp_path, parent_sha256=digest, version="v1.1")
    assert (tmp_path / updated["parent_manifest"]["file"]).read_bytes() == original
    assert verify_manifest(tmp_path) == []


def test_frozen_recent_csv_contract_uniqueness_and_coverage():
    from collections import Counter
    from pathlib import Path
    from scayl.ingest.validate import load_snapshot
    from scayl.ingest.manifest import verify_manifest
    root = Path("data/raw/v1")
    _, indicators, _, _ = load_snapshot(root)
    recent = [o for o in indicators if o.fuente in ("acp", "inec")]
    assert len(recent) == len({(o.indicador_id, o.periodo) for o in recent}) == 812
    assert Counter(o.indicador_id for o in recent) == {
        "ACP.GATUN.NIVEL": 394, "ACP.GATUN.PROYECCION": 394,
        "INEC.IPC.VAR_MENSUAL": 12, "INEC.IPC.VAR_INTERANUAL": 12}
    assert all(o.periodo < "2026-10-01" for o in recent)
    assert all(o.valor is None and o.es_proyeccion for o in recent if o.indicador_id == "ACP.GATUN.PROYECCION")
    assert verify_manifest(root) == []
