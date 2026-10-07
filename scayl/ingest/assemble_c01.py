"""Assemble C-01 headlines from immutable response files, with exclusions."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

from .common import json_bytes, utc_now, write_csv, write_once
from .fetch_gdelt import FIELDS, article_row
from .fetch_gkg import extract
from .fetch_tvn import historical_rows
from .window import news_window


def collect(directory: Path) -> tuple[list[dict], dict]:
    start, end = news_window()
    selected: dict[str, dict] = {}
    excluded: list[dict] = []
    sources: list[dict] = []
    # RSS first: a publication date takes precedence over an aggregator detection.
    feed = json.loads((directory / "tvn_rss_actual.json").read_text(encoding="utf-8"))
    rss = historical_rows(feed["items"], start, end)
    for item in feed["items"]:
        if not start <= parsedate_to_datetime(item["fecha_publicacion_original"]) < end:
            excluded.append({"file": "tvn_rss_actual.json", "url": item["url"],
                             "reason": "fuera_de_ventana_C-01"})
    for row in rss:
        selected[row["url"]] = row
    sources.append({"file": "tvn_rss_actual.json", "selected": len(rss),
                    "excluded": len(feed["items"]) - len(rss)})
    for path in sorted((directory / "responses/gdelt").glob("*.json")):
        if path.name.endswith(".request.json"):
            continue
        receipt = json.loads(path.with_name(path.name + ".request.json").read_text(encoding="utf-8"))
        try:
            payload = json.loads(path.read_bytes())
            if not isinstance(payload, dict) or (payload and "articles" not in payload):
                raise ValueError("DOC response missing articles")
            records = [article_row(a, receipt["fecha_extraccion"]) for a in payload.get("articles", [])]
        except (ValueError, KeyError, TypeError) as error:
            excluded.append({"file": path.relative_to(directory).as_posix(), "reason": "respuesta_invalida", "detail": str(error)})
            continue
        sources.append({"file": path.relative_to(directory).as_posix(), "records": len(records)})
        for row in records:
            detected = datetime.fromisoformat(row["fecha_deteccion"])
            reason = ("fuera_de_ventana_C-01" if not start <= detected < end else
                      "duplicado_url" if row["url"] in selected else None)
            if reason:
                excluded.append({"file": path.relative_to(directory).as_posix(),
                                 "id_noticia": row["id_noticia"], "reason": reason})
            else:
                selected[row["url"]] = row
    for path in sorted((directory / "responses/gkg").glob("*.zip")):
        detected = datetime.strptime(path.name[:14], "%Y%m%d%H%M%S").replace(tzinfo=start.tzinfo)
        name = path.relative_to(directory).as_posix()
        if not start <= detected < end:
            excluded.append({"file": name, "reason": "fuera_de_ventana_C-01"})
            continue
        receipt = json.loads(path.with_name(path.name + ".request.json").read_text(encoding="utf-8"))
        invalid: list[dict] = []
        records = extract(path.read_bytes(), receipt["fecha_extraccion"], invalid)
        excluded.extend({"file": name, **entry} for entry in invalid)
        sources.append({"file": name, "records": len(records), "method": "GKG sample, not exhaustive"})
        for row in records:
            when = datetime.fromisoformat(row["fecha_deteccion"])
            if not start <= when < end:
                excluded.append({"file": name, "id_noticia": row["id_noticia"], "reason": "fuera_de_ventana_C-01"})
            elif row["url"] in selected:
                excluded.append({"file": name, "id_noticia": row["id_noticia"], "reason": "duplicado_url"})
            else:
                selected[row["url"]] = row
    rows = sorted(selected.values(), key=lambda row: row["id_noticia"])
    report = {"created_at": utc_now(), "window": [start.isoformat(), end.isoformat()],
              "news": len(rows), "tvn": sum(row["medio"] == "TVN" for row in rows),
              "sources": sources, "excluded": excluded,
              "effective_start": min((r["fecha_publicacion"] or r["fecha_deteccion"] for r in rows), default=None),
              "effective_end": max((r["fecha_publicacion"] or r["fecha_deteccion"] for r in rows), default=None)}
    for name, window_start in (("target_30_days", news_window(target=True)[0]),
                               ("extended_90_days", news_window(extended=True)[0])):
        recent = [r for r in rows if datetime.fromisoformat(r["fecha_publicacion"] or r["fecha_deteccion"]) >= window_start]
        report[name] = {"news": len(recent), "tvn": sum(r["medio"] == "TVN" for r in recent)}
    return rows, report


def assemble(directory: Path) -> dict:
    if (directory / "manifest.json").exists():
        from .manifest import verify_manifest
        differences = verify_manifest(directory)
        if differences:
            raise ValueError(f"Frozen snapshot changed: {differences}")
        return json.loads((directory / "assembly-c01.json").read_text(encoding="utf-8"))
    rows, report = collect(directory)
    if report["news"] < 100 or report["tvn"] < 20:
        raise ValueError(f"Coverage incomplete: {report['news']} news, {report['tvn']} TVN")
    if report["extended_90_days"]["news"] < 100 or report["extended_90_days"]["tvn"] < 20:
        raise ValueError(f"Recent coverage incomplete: {report['extended_90_days']}")
    if not (directory / "eventos_ext.geojson").exists():
        raise ValueError("USGS extension missing")
    write_once(directory / "assembly-c01.json", json_bytes(report))
    write_csv(directory / "noticias.csv", rows, FIELDS)
    sources = [
        {"origen": "gdelt", "url": "https://api.gdeltproject.org/api/v2/doc/doc",
         "licencia": "Metadatos; derechos de titulares de cada medio", "alcance": "titular_metadatos",
         "limitaciones": "Muestreo DOC/GKG no exhaustivo; publicación desconocida, detección no es publicación.",
         "cobertura": report["window"]},
        {"origen": "tvn_rss", "url": "https://www.tvn-2.com/rss/",
         "licencia": "Sin licencia abierta de artículos; solo titulares y enlaces",
         "limitaciones": "Publicación declarada por pubDate; detección nula; feed parcial, cobertura C-01 completa admitida por DL-017."},
        {"origen": "wb", "url": "https://api.worldbank.org/v2", "licencia": "CC BY 4.0 salvo excepciones por indicador",
         "cobertura": "2010-2024, seis países, seis indicadores, 540 filas", "limitaciones": "Contexto histórico, no condiciones actuales."},
        {"origen": "usgs", "url": "https://earthquake.usgs.gov/fdsnws/event/1/query",
         "licencia": "Dominio público USGS, salvo contenido de terceros", "cobertura": "2024 oficial + extensión ventana C-01 (AP-004)",
         "limitaciones": "Caja lat 5..12, lon -86..-76; M>=3; la caja no equivale al territorio de Panamá."},
    ]
    write_once(directory / "fuentes.json", json_bytes(sources))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    result = collect(args.directory)[1] if args.inspect else assemble(args.directory)
    print(json.dumps({k: v for k, v in result.items() if k not in ("sources", "excluded")}, indent=2))
