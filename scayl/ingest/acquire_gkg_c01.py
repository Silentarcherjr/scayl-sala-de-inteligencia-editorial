"""C-01 fallback after DOC rate limiting: declared daily GKG samples."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import timedelta
from pathlib import Path

from .common import download, json_bytes, utc_now, write_once
from .fetch_gkg import extract
from .window import news_window


def acquire(directory: Path, *, extended: bool = False) -> dict:
    start, end = news_window(target=True, extended=extended)
    batches = []
    rows = {}
    local = {}
    failures = 0
    day = start
    while day < end:
        name = day.strftime("%Y%m%d") + "180000.translation.gkg.csv.zip"
        try:
            content, meta = download(directory / "responses/gkg", name,
                                     "https://data.gdeltproject.org/gdeltv2/" + name)
            invalid = []
            selected = extract(content, meta["fecha_extraccion"], invalid)
            for row in selected:
                when = row["fecha_deteccion"][:10]
                if not start.date().isoformat() <= when < end.date().isoformat():
                    raise ValueError("GKG detection outside requested window")
                rows.setdefault(row["url"], row)
            local["responses/gkg/" + name] = {"sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content), "disponibilidad": "solo local"}
            batches.append({"file": name, "selected": len(selected), "excluded": invalid})
            print(f"{name}: {len(selected)} selected; {len(rows)} unique", flush=True)
            failures = 0
        except (OSError, ValueError) as error:
            batches.append({"file": name, "error": str(error)})
            failures += 1
            print(f"{name}: {error}", flush=True)
        if failures >= 3:
            break
        day += timedelta(days=1)
    stamp = utc_now().replace(":", "").replace("-", "")
    report = {"at": utc_now(), "start": start.isoformat(), "end_exclusive": end.isoformat(),
              "method": "Daily 18:00 UTC GKG translation sample; not exhaustive",
              "reason": "DOC rate limiting (HTTP 429), DL-008 fallback",
              "unique": len(rows), "batches": batches, "complete": day >= end}
    write_once(directory / f"gkg-c01-{stamp}.json", json_bytes(report))
    write_once(directory / f"acquisition_inventory.c01-{stamp}.json", json_bytes({
        "status": "local_acquisition_provenance", "created_at": utc_now(), "files": local}))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/v1"))
    parser.add_argument("--extended", action="store_true")
    args = parser.parse_args()
    acquire(args.output, extended=args.extended)
