import csv

import pytest

from scayl.eval.support_review import export, measure


def sample(bundle, tmp_path):
    first = bundle.packages[0]
    sentence = first.brief[0]
    bundle.packages = [first.model_copy(update={"package_id": f"PKG-{i}", "brief": [
        sentence.model_copy(update={"text": f"[SINTÉTICO] Afirmación de prueba {i}"})], "script": []})
        for i in range(30)]
    source = tmp_path / "bundle.json"
    source.write_text(bundle.model_dump_json(), encoding="utf-8")
    output = tmp_path / "support.csv"
    export(source, output)
    return source, output


def edit(path, update):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    update(rows)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_blank_labels_are_unmeasured_and_export_never_overwrites(bundle, tmp_path):
    source, path = sample(bundle, tmp_path)
    result = measure(path)
    assert result["status"] == "no medido" and result["num"] is None and result["reviewed"] == 0
    with pytest.raises(ValueError, match="sobrescribir"):
        export(source, path)


def test_partial_counts_as_not_fully_supported_and_needs_complete_sample(bundle, tmp_path):
    _, path = sample(bundle, tmp_path)
    def label(rows):
        for row in rows:
            row.update(decision="sí", reviewer="Revisor sintético de prueba", reviewed_at_utc="2026-10-07T17:00:00Z")
        rows[0]["decision"] = "parcial"
        rows[1]["decision"] = "no"
    edit(path, label)
    result = measure(path)
    assert result["num"] == 28 and result["den"] == 30 and len(result["failures"]) == 2
    edit(path, lambda rows: rows[2].update(decision=""))
    assert measure(path)["status"] == "no medido"


def test_evidence_tampering_and_missing_reviewer_are_rejected(bundle, tmp_path):
    _, path = sample(bundle, tmp_path)
    edit(path, lambda rows: rows[0].update(decision="sí"))
    with pytest.raises(ValueError, match="revisor"):
        measure(path)
    edit(path, lambda rows: rows[0].update(statement="changed"))
    with pytest.raises(ValueError, match="cambiaron"):
        measure(path)
