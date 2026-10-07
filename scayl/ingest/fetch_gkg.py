"""Documented DL-008 fallback: sample historical GKG 2.1 metadata batches."""
from __future__ import annotations

import argparse
import html
import io
import re
import zipfile
from datetime import date, timedelta
from pathlib import Path

from .common import download, json_bytes, write_csv, write_once
from .fetch_gdelt import FIELDS, article_row
from .window import news_window


def extract(content: bytes, extracted: str, excluded: list[dict] | None = None) -> list[dict]:
    rows = []
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for member in archive.namelist():
            with archive.open(member) as handle:
                for line_number, raw_line in enumerate(handle, 1):
                    try:
                        line = raw_line.decode("utf-8")
                    except UnicodeDecodeError:
                        if excluded is not None:
                            excluded.append({"member": member, "line": line_number, "reason": "invalid_utf8"})
                        continue
                    fields = line.rstrip("\n").split("\t")
                    if len(fields) < 27:
                        if excluded is not None:
                            excluded.append({"member": member, "line": line_number, "reason": "fewer_than_27_fields"})
                        continue
                    title_match = re.search(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", fields[26])
                    if not title_match:
                        continue
                    title = html.unescape(title_match.group(1)).strip()
                    tvn = fields[3] in ("tvn-2.com", "www.tvn-2.com")
                    # GKG location country code PM is Panama. Do not infer it from a person's name.
                    panama = bool(re.search(r"(?:^|;)\d+#[^#]*#PM#", fields[9]))
                    if not tvn and not (panama and re.search(r"panam[aá]", title, re.IGNORECASE)):
                        continue
                    detected = fields[1][:8] + "T" + fields[1][8:14] + "Z"
                    language = re.search(r"srclc:([^;]+)", fields[25])
                    row = article_row({"url": fields[4], "title": title, "domain": fields[3],
                                       "seendate": detected, "language": language.group(1) if language else None}, extracted)
                    rows.append(row)
    return rows


def fetch(directory: Path, start: date, end: date) -> list[dict]:
    rows = {}
    batches = []
    # Stratified by day and UTC hour, deterministic plan. Stop after documented minimums.
    for hour in (18, 0, 21):
        day = start
        while day < end:
            stamp = day.strftime("%Y%m%d") + f"{hour:02}0000"
            name = stamp + ".translation.gkg.csv.zip"
            content, meta = download(directory / "responses/gkg", name,
                                     "https://data.gdeltproject.org/gdeltv2/" + name)
            excluded = []
            selected = extract(content, meta["fecha_extraccion"], excluded)
            for row in selected:
                if not start.isoformat() <= row["fecha_deteccion"][:10] < end.isoformat():
                    raise ValueError("GKG record outside requested interval")
                rows.setdefault(row["url"], row)
            batches.append({"file": name, "selected": len(selected), "excluded": excluded})
            tvn = sum(row["medio"] == "TVN" for row in rows.values())
            print(f"{stamp}: selected={len(selected)} unique={len(rows)} tvn={tvn}", flush=True)
            day += timedelta(days=1)
        if len(rows) >= 100 and tvn >= 20:
            break
    result = sorted(rows.values(), key=lambda row: row["id_noticia"])
    report = {"method": "GKG 2.1 fallback; deterministic stratified batches, not exhaustive coverage",
              "start": start.isoformat(), "end_exclusive": end.isoformat(), "batches": batches,
              "unique": len(rows), "tvn": tvn,
              "reason": "DOC API returned repeated HTTP 429; use DL-008 historical GKG fallback"}
    write_once(directory / "gkg-run.json", json_bytes(report))
    if len(rows) < 100 or tvn < 20:
        raise ValueError("Historical fallback minimums not met")
    write_csv(directory / "noticias.csv", result, FIELDS)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/v1"))
    start, end = news_window(target=True)
    parser.add_argument("--start", type=date.fromisoformat, default=start.date())
    parser.add_argument("--end", type=date.fromisoformat, default=end.date())
    args = parser.parse_args()
    fetch(args.output, args.start, args.end)
