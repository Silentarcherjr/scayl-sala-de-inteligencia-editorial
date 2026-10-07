"""Keep the current TVN RSS separately; never mix it with historical news."""
from __future__ import annotations

import argparse
import hashlib
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

from .common import download, json_bytes, write_once
from .fetch_gdelt import normalize_url


def historical_rows(items: list[dict], start: datetime, end: datetime) -> list[dict]:
    """Select RSS publication dates in the C-01 window (DL-017/DL-022)."""
    rows = {}
    for item in items:
        published = parsedate_to_datetime(item["fecha_publicacion_original"])
        if published.tzinfo is None:
            raise ValueError("RSS publication must include a timezone")
        published = published.astimezone(UTC)
        if not start <= published < end:
            continue
        url = normalize_url(item["url"])
        rows.setdefault(url, {"id_noticia": "tvn-" + hashlib.sha256(url.encode()).hexdigest()[:20],
                             "titulo": item["titulo"], "url": url, "medio": "TVN", "idioma": "es",
                             "fecha_publicacion": published.isoformat().replace("+00:00", "Z"),
                             "fecha_deteccion": None,
                             "fecha_extraccion": item["fecha_extraccion"], "tema": None,
                             "origen": "tvn_rss", "alcance_texto": "titular_metadatos",
                             "licencia": "Titulares y enlaces TVN; sin licencia abierta sobre artículos o imágenes"})
    return sorted(rows.values(), key=lambda row: row["id_noticia"])


def fetch(directory: Path, url: str) -> list[dict]:
    content, meta = download(directory / "responses/tvn-current", "rss.xml", url)
    root = ET.fromstring(content)
    rows = [{"titulo": item.findtext("title"), "url": item.findtext("link"),
             "fecha_publicacion_original": item.findtext("pubDate"),
             "fecha_extraccion": meta["fecha_extraccion"]}
            for item in root.findall(".//item")]
    if not rows:
        raise ValueError("TVN RSS has no items")
    write_once(directory / "tvn_rss_actual.json", json_bytes({"fuera_del_snapshot": True, "items": rows}))
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/v1"))
    parser.add_argument("--url", required=True, help="Public RSS endpoint verified on TVN")
    args = parser.parse_args()
    fetch(args.output, args.url)
