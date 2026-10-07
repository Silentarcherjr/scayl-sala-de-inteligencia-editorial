"""World Bank WDI: explicit six-country, six-indicator, fifteen-year grid."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import download, write_csv

COUNTRIES = ("PAN", "CRI", "COL", "DOM", "MEX", "GTM")
INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "% anual",
    "FP.CPI.TOTL.ZG": "% anual",
    "SL.UEM.TOTL.ZS": "% de la población activa total (estimación modelada OIT)",
    "SP.POP.TOTL": "personas",
    "IT.NET.USER.ZS": "% de la población",
    "NE.EXP.GNFS.ZS": "% del PIB",
}
FIELDS = ["pais_iso3", "indicador_id", "indicador_nombre", "anio", "valor", "unidad",
          "fuente_url", "fecha_extraccion", "licencia"]


def complete_grid(records: list[dict], indicator: str, extracted: str, url: str) -> list[dict]:
    observations = {}
    for record in records:
        key = (record["countryiso3code"], int(record["date"]))
        if key in observations:
            raise ValueError(f"Duplicate World Bank observation: {key}")
        observations[key] = record
    names = {r["indicator"]["value"] for r in records}
    name = next(iter(names)) if len(names) == 1 else None
    return [{"pais_iso3": country, "indicador_id": indicator, "indicador_nombre": name,
             "anio": year, "valor": observations.get((country, year), {}).get("value"),
             "unidad": INDICATORS[indicator], "fuente_url": url, "fecha_extraccion": extracted,
             "licencia": "CC BY 4.0 (World Development Indicators; atribución World Bank)"}
            for country in COUNTRIES for year in range(2010, 2025)]


def fetch(directory: Path) -> list[dict]:
    rows = []
    for indicator in INDICATORS:
        url = f"https://api.worldbank.org/v2/country/{';'.join(COUNTRIES)}/indicator/{indicator}"
        records = []
        page = 1
        while True:
            content, meta = download(directory / "responses/worldbank", f"{indicator}.{page}.json", url,
                                     {"format": "json", "date": "2010:2024", "per_page": 1000, "page": page, "source": 2})
            payload = json.loads(content)
            if not isinstance(payload, list) or len(payload) != 2 or not isinstance(payload[0], dict):
                raise ValueError(f"World Bank error: {indicator}")
            records.extend(payload[1] or [])
            if page >= int(payload[0]["pages"]):
                break
            page += 1
        rows.extend(complete_grid(records, indicator, meta["fecha_extraccion"], url))
    write_csv(directory / "indicadores.csv", rows, FIELDS)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/v1"))
    fetch(parser.parse_args().output)
