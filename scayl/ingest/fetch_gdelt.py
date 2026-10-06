"""Daily GDELT DOC requests; headlines and metadata only, deduplicated by URL."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from .common import download, json_bytes, utc_now, write_csv, write_once

QUERIES = {
    "tvn": "domain:tvn-2.com",
    "canal": '(Panama OR Panamá) (canal OR logistics OR logística)',
    "turismo": '(Panama OR Panamá) (tourism OR turismo)',
    "economia": '(Panama OR Panamá) (economy OR economía)',
    "naturales": '(Panama OR Panamá) (earthquake OR sismo OR inundaciones OR flood)',
}
FIELDS = ["id_noticia", "titulo", "url", "medio", "idioma", "fecha_publicacion",
          "fecha_deteccion", "fecha_extraccion", "tema", "origen", "alcance_texto", "licencia"]


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
        raise ValueError("Invalid article URL")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", parts.query, ""))


def article_row(article: dict, extracted: str) -> dict:
    url = normalize_url(article["url"])
    seen = datetime.strptime(article["seendate"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    domain = urlsplit(url).hostname or ""
    return {"id_noticia": "gdt-" + hashlib.sha256(url.encode()).hexdigest()[:20],
            "titulo": article["title"], "url": url,
            "medio": "TVN" if domain == "tvn-2.com" or domain.endswith(".tvn-2.com") else article.get("domain") or domain,
            "idioma": article.get("language"), "fecha_publicacion": None,
            "fecha_deteccion": seen.isoformat().replace("+00:00", "Z"), "fecha_extraccion": extracted,
            "tema": None, "origen": "gdelt", "alcance_texto": "titular_metadatos",
            "licencia": "Metadatos GDELT; derechos de los titulares corresponden a cada medio"}


def fetch(directory: Path, start: date, end: date, delay: float = 6) -> list[dict]:
    """Only freeze noticias.csv after the complete query plan succeeds."""
    rows: dict[str, dict] = {}
    failures = []
    day = start
    while day < end:
        for label, query in QUERIES.items():
            name = f"{day.isoformat()}.{label}.json"
            params = {"query": query, "mode": "ArtList", "format": "json", "maxrecords": 250,
                      "STARTDATETIME": day.strftime("%Y%m%d") + "000000",
                      "ENDDATETIME": day.strftime("%Y%m%d") + "235959"}
            try:
                content, meta = download(directory / "responses/gdelt", name,
                                         "https://api.gdeltproject.org/api/v2/doc/doc", params)
                payload = json.loads(content)
                articles = payload.get("articles", [])
                if not isinstance(articles, list) or ("articles" not in payload and payload):
                    raise ValueError("Unexpected GDELT payload")
                for article in articles:
                    row = article_row(article, meta["fecha_extraccion"])
                    detected = row["fecha_deteccion"][:10]
                    if not start.isoformat() <= detected < end.isoformat():
                        raise ValueError("GDELT returned an article outside the requested interval")
                    rows.setdefault(row["url"], row)
                print(f"{name}: {len(articles)} articles; {len(rows)} unique", flush=True)
            except (OSError, ValueError, KeyError, TypeError) as error:
                failures.append({"query": params, "error": str(error), "at": utc_now()})
                print(f"{name}: {type(error).__name__}: {error}", flush=True)
            time.sleep(delay)
        day += timedelta(days=1)
    report = {"start": start.isoformat(), "end_exclusive": end.isoformat(), "unique": len(rows),
              "tvn": sum(row["medio"] == "TVN" for row in rows.values()), "failures": failures}
    write_once(directory / f"gdelt-run-{start}-{end}.json", json_bytes(report))
    if failures:
        # Partial results remain in immutable response files for diagnosis/recovery.
        raise RuntimeError(f"{len(failures)} GDELT queries failed; snapshot not frozen")
    result = sorted(rows.values(), key=lambda row: row["id_noticia"])
    write_csv(directory / "noticias.csv", result, FIELDS)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/v1"))
    parser.add_argument("--start", type=date.fromisoformat, default=date(2025, 9, 1))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2025, 10, 1))
    args = parser.parse_args()
    fetch(args.output, args.start, args.end)
