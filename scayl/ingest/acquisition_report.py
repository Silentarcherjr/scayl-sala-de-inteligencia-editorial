"""Audit already downloaded responses without network or publication decisions."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from .common import json_bytes, utc_now, write_once
from .fetch_gdelt import article_row
from .fetch_gkg import extract


def audit(directory: Path) -> dict:
    gdelt_rows = {}
    responses = []
    for path in sorted((directory / "responses/gdelt").glob("*.json")):
        if path.name.endswith(".request.json"):
            continue
        receipt = json.loads(path.with_name(path.name + ".request.json").read_text(encoding="utf-8"))
        payload = json.loads(path.read_bytes())
        rows = [article_row(article, receipt["fecha_extraccion"]) for article in payload.get("articles", [])]
        for row in rows:
            gdelt_rows.setdefault(row["url"], row)
        responses.append({"file": path.relative_to(directory).as_posix(), "records": len(rows)})
    gkg_rows = {}
    gkg_batches = []
    for path in sorted((directory / "responses/gkg").glob("*.zip")):
        receipt = json.loads(path.with_name(path.name + ".request.json").read_text(encoding="utf-8"))
        excluded = []
        rows = extract(path.read_bytes(), receipt["fecha_extraccion"], excluded)
        for row in rows:
            gkg_rows.setdefault(row["url"], row)
        gkg_batches.append({"file": path.relative_to(directory).as_posix(), "selected": len(rows), "excluded": excluded})
    rss = json.loads((directory / "tvn_rss_actual.json").read_text(encoding="utf-8"))["items"]
    start, end = datetime(2024, 1, 1, tzinfo=timezone.utc), datetime(2025, 10, 1, tzinfo=timezone.utc)
    historical = [row for row in rss if start <= parsedate_to_datetime(row["fecha_publicacion_original"]) < end]
    with (directory / "indicadores.csv").open(encoding="utf-8", newline="") as handle:
        indicators = list(csv.DictReader(handle))
    quakes = json.loads((directory / "eventos.geojson").read_text(encoding="utf-8"))["features"]
    all_news = {**gkg_rows, **gdelt_rows}
    return {"created_at": utc_now(), "status": "acquisition_in_progress_not_frozen",
            "gdelt_doc": {"unique": len(gdelt_rows), "tvn": sum(r["medio"] == "TVN" for r in gdelt_rows.values()), "responses": responses},
            "gdelt_gkg": {"unique": len(gkg_rows), "tvn": sum(r["medio"] == "TVN" for r in gkg_rows.values()), "batches": gkg_batches},
            "combined_gdelt_unique": len(all_news),
            "rss": {"total": len(rss), "within_official_interval": len(historical), "incorporated_in_news": False,
                    "decision_required": "AP-009"},
            "worldbank": {"rows": len(indicators), "nulls": sum(r["valor"] == "null" for r in indicators),
                          "dimensions": "6 countries x 6 indicators x 15 years", "decision_required": "AP-008"},
            "usgs": {"events": len(quakes)}, "proposals_pending": ["AP-008", "AP-009"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.directory)
    write_once(args.output, json_bytes(report))
    print(json.dumps({key: value for key, value in report.items() if key not in ("gdelt_doc", "gdelt_gkg")}, indent=2))
