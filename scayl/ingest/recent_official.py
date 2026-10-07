"""Deterministic ACP CSV adapters and audited INEC PDF transcription (B-13/B-14)."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from .common import write_csv

FIELDS = ["pais_iso3", "indicador_id", "indicador_nombre", "anio", "valor", "unidad",
          "fuente_url", "fecha_extraccion", "licencia", "periodo", "fuente", "frecuencia",
          "es_proyeccion"]


def acp_history(content: bytes, start: date, end: date) -> dict[str, float | None]:
    """Half-open interval; tolerate ACP's CRCRLF without changing the raw bytes."""
    result = {}
    for row in csv.DictReader(io.StringIO(content.decode("utf-8-sig"), newline=None)):
        when = date.fromisoformat(row["DATE_LOG"].strip())
        if start <= when < end:
            key = when.isoformat()
            if key in result:
                raise ValueError(f"Duplicate ACP period: {key}")
            value = row["GATUN_LAKE_LEVEL(FEET)"].strip()
            result[key] = float(value) if value else None
    return result


def acp_projections(content: bytes, start: date, end: date, *,
                    published_at: datetime | None, cutoff: datetime) -> dict[str, float | None]:
    """Never admit a forecast without evidence that it was issued before the cutoff."""
    if published_at is None or published_at >= cutoff:
        return {}
    lines = content.decode("utf-8-sig").splitlines()
    header = next(i for i, line in enumerate(lines) if line.startswith("projected_date,"))
    result = {}
    for row in csv.DictReader(lines[header:]):
        when = datetime.strptime(row["projected_date"].strip(), "%m/%d/%Y").date()
        if start <= when < end:
            key = when.isoformat()
            if key in result:
                raise ValueError(f"Duplicate ACP projection: {key}")
            value = row["projected_gatun_water_level"].strip()
            result[key] = float(value) if value else None
    return result


def daily_rows(values: dict[str, float | None], start: date, end: date, *,
               series: str, name: str, receipt: dict, projection: bool) -> list[dict]:
    """Explicit nulls for missing daily observations/forecasts; no interpolation."""
    rows = []
    day = start
    while day < end:
        rows.append(dict(pais_iso3="PAN", indicador_id=series, indicador_nombre=name,
                         anio=day.year, valor=values.get(day.isoformat()), unidad="pies",
                         fuente_url=receipt["url"], fecha_extraccion=receipt["fecha_extraccion"],
                         licencia="ACP: uso informativo; sin licencia abierta declarada",
                         periodo=day.isoformat(), fuente="acp", frecuencia="diaria",
                         es_proyeccion="true" if projection else "false"))
        day += timedelta(days=1)
    return rows


def inec_transcription(pdf: bytes, transcription: dict, receipt: dict,
                       cutoff: datetime) -> list[dict]:
    """Check the PDF fingerprint, publication date and signed values copied from its table."""
    if hashlib.sha256(pdf).hexdigest() != transcription["pdf_sha256"]:
        raise ValueError("INEC transcription belongs to a different PDF")
    if datetime.fromisoformat(transcription["published_at"]) >= cutoff:
        raise ValueError("INEC publication is after the cutoff")
    rows, seen = [], set()
    for item in transcription["rows"]:
        period = item["periodo"]
        when = date.fromisoformat(period + "-01")
        if not ("2025-09" <= period < cutoff.strftime("%Y-%m")):
            raise ValueError(f"INEC period outside requested window: {period}")
        if period in seen:
            raise ValueError(f"Duplicate INEC period: {period}")
        seen.add(period)
        for suffix, key in [("MENSUAL", "mensual"), ("INTERANUAL", "interanual")]:
            rows.append(dict(pais_iso3="PAN", indicador_id=f"INEC.IPC.VAR_{suffix}",
                             indicador_nombre=f"IPC nacional urbano, variación {key}; Anexo 4, página PDF 1",
                             anio=when.year, valor=item[key], unidad="%", fuente_url=receipt["url"] + "#page=1",
                             fecha_extraccion=receipt["fecha_extraccion"], licencia="CC BY 4.0",
                             periodo=period, fuente="inec", frecuencia="mensual", es_proyeccion="false"))
    return rows


def assemble(directory: Path) -> list[dict]:
    """Reproduce C-01's CSV from frozen source bytes/receipts, without network access."""
    start, end = date(2025, 9, 2), date(2026, 10, 1)
    cutoff = datetime.fromisoformat("2026-10-01T00:00:00+00:00")
    def source(folder: str, name: str) -> tuple[bytes, dict]:
        p = directory / "responses" / folder / name
        return p.read_bytes(), json.loads(p.with_name(p.name + ".request.json").read_text(encoding="utf-8"))
    history, receipt = source("acp", "gatun-history.csv")
    rows = daily_rows(acp_history(history, start, end), start, end, series="ACP.GATUN.NIVEL",
                      name="Nivel observado del lago Gatún", receipt=receipt, projection=False)
    projection, receipt = source("acp", "gatun-projection.csv")
    values = acp_projections(projection, start, end, published_at=None, cutoff=cutoff)
    rows += daily_rows(values, start, end, series="ACP.GATUN.PROYECCION",
                       name="Proyección del lago Gatún; ausente al corte, no reconstruida",
                       receipt=receipt, projection=True)
    pdf, receipt = source("inec", "ipc-anexo4-2026-08.pdf")
    transcription = json.loads((directory / "responses/inec/ipc-anexo4-2026-08.transcription.json")
                               .read_text(encoding="utf-8"))
    rows += inec_transcription(pdf, transcription, receipt, cutoff)
    write_csv(directory / "indicadores_recientes.csv", rows, FIELDS)
    return rows


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, nargs="?", default=Path("data/raw/v1"))
    print(f"rows: {len(assemble(parser.parse_args().directory))}")
