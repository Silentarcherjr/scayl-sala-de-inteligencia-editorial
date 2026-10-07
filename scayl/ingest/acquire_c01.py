"""Bounded daily DOC acquisition for C-01; raw responses are always immutable."""
from __future__ import annotations

import argparse
import json
import time
from datetime import timedelta
from pathlib import Path

from .common import download, json_bytes, utc_now, write_once
from .fetch_gdelt import QUERIES, article_row
from .window import news_window


def acquire(directory: Path, *, extended: bool = False) -> dict:
    start, end = news_window(target=True, extended=extended)
    day = start
    attempts: list[dict] = []
    consecutive_failures = 0
    rows: dict[str, dict] = {}
    while day < end:
        for label, query in QUERIES.items():
            name = f"{day.date()}.{label}.json"
            params = {"query": query, "mode": "ArtList", "format": "json", "maxrecords": 250,
                      "STARTDATETIME": day.strftime("%Y%m%d") + "000000",
                      "ENDDATETIME": day.strftime("%Y%m%d") + "235959"}
            try:
                content, meta = download(directory / "responses/gdelt", name,
                                         "https://api.gdeltproject.org/api/v2/doc/doc", params)
                payload = json.loads(content)
                if not isinstance(payload, dict) or not isinstance(payload.get("articles", []), list):
                    raise ValueError("Unexpected DOC payload")
                if payload and "articles" not in payload:
                    raise ValueError("DOC response has no articles field")
                selected = [article_row(a, meta["fecha_extraccion"]) for a in payload.get("articles", [])]
                for row in selected:
                    if not start.isoformat()[:10] <= row["fecha_deteccion"][:10] < end.isoformat()[:10]:
                        raise ValueError("DOC article outside requested window")
                    rows.setdefault(row["url"], row)
                attempts.append({"file": name, "records": len(selected), "success": True})
                consecutive_failures = 0
                print(f"{name}: {len(selected)} records; {len(rows)} unique", flush=True)
            except (OSError, ValueError, KeyError, TypeError) as error:
                attempts.append({"file": name, "success": False, "error": str(error)})
                consecutive_failures += 1
                print(f"{name}: {type(error).__name__}: {error}", flush=True)
            if consecutive_failures >= 3:
                break
            time.sleep(6)
        if consecutive_failures >= 3:
            break
        day += timedelta(days=1)
    result = {"at": utc_now(), "start": start.isoformat(), "end_exclusive": end.isoformat(),
              "attempts": attempts, "unique": len(rows),
              "complete": day >= end, "stopped_after_consecutive_failures": consecutive_failures >= 3}
    stamp = result["at"].replace(":", "").replace("-", "")
    write_once(directory / f"doc-c01-{stamp}.json", json_bytes(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/v1"))
    parser.add_argument("--extended", action="store_true")
    args = parser.parse_args()
    acquire(args.output, extended=args.extended)
