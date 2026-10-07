"""B-03 / T01: load a frozen snapshot into contract objects without rejecting the whole dataset.

    news, indicators, quakes, report = load_snapshot(Path("data/raw/v1"))

Rules (ARCHITECTURE §4.1):
- NULL stays None (CSV token "null" or empty); never 0 or "".
- Invalid dates -> None + quality flag; the row is kept.
- Missing id_noticia or titulo -> row excluded with a reason (never silently dropped).
- Out of the C-01 news window (scayl/config/data_window.v1.yaml) by publication date, or by detection
  date when publication is unknown -> excluded with reason ``fuera_de_intervalo``.
- Duplicate normalized URL -> first kept, later rows excluded with reason ``url_duplicada``.
- Language codes normalized to ISO 639-1 (original kept in a quality flag when changed).
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import yaml

from scayl.contracts import IndicatorObservation, NewsItem, Origin, SeismicEvent, TextScope, Topic

NULL_TOKENS = {"", "null", "None", "NULL", "NaN", "nan"}
LANG = {"spa": "es", "spanish": "es", "es": "es", "español": "es", "eng": "en", "english": "en", "en": "en",
        "fra": "fr", "french": "fr", "fr": "fr", "por": "pt", "portuguese": "pt", "pt": "pt",
        "ita": "it", "italian": "it", "deu": "de", "german": "de"}
WINDOW_FILE = Path(__file__).resolve().parents[1] / "config" / "data_window.v1.yaml"


@dataclass
class QualityReport:
    total: int = 0
    valid: int = 0
    excluded: list[dict] = field(default_factory=list)
    excluded_by_reason: Counter = field(default_factory=Counter)
    flags: Counter = field(default_factory=Counter)
    nulls_by_field: Counter = field(default_factory=Counter)
    indicators: int = 0
    indicators_null_values: int = 0
    seismic_official: int = 0
    seismic_extension: int = 0

    def exclude(self, row_ref: str, reason: str, detail: str = "") -> None:
        self.excluded.append({"ref": row_ref, "reason": reason, "detail": detail})
        self.excluded_by_reason[reason] += 1

    def to_dict(self) -> dict:
        return {"total": self.total, "valid": self.valid, "excluded_by_reason": dict(self.excluded_by_reason),
                "excluded": self.excluded, "flags": dict(self.flags), "nulls_by_field": dict(self.nulls_by_field),
                "indicators": self.indicators, "indicators_null_values": self.indicators_null_values,
                "seismic_official": self.seismic_official, "seismic_extension": self.seismic_extension}


def _null(value: str | None) -> str | None:
    return None if value is None or value.strip() in NULL_TOKENS else value.strip()


def _date(value: str | None) -> tuple[datetime | None, bool]:
    """(parsed UTC datetime or None, invalid?)"""
    raw = _null(value)
    if raw is None:
        return None, False
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None, True
    return (dt if dt.tzinfo else dt.replace(tzinfo=UTC)).astimezone(UTC), False


def _norm_url(url: str | None) -> str | None:
    if not url:
        return None
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower().removeprefix("www."), parts.path.rstrip("/"),
                       parts.query, ""))


def news_window(path: Path = WINDOW_FILE) -> tuple[datetime, datetime]:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))["news"]
    return (datetime.fromisoformat(cfg["start_inclusive"]), datetime.fromisoformat(cfg["end_exclusive"]))


def load_news(path: Path, report: QualityReport, window: tuple[datetime, datetime] | None = None) -> list[NewsItem]:
    start, end = window or news_window()
    seen_urls: set[str] = set()
    out: list[NewsItem] = []
    with path.open(encoding="utf-8", newline="") as fh:
        for line_no, row in enumerate(csv.DictReader(fh), start=2):
            report.total += 1
            ref = f"{path.name}:{line_no}"
            for key, value in row.items():
                if _null(value) is None:
                    report.nulls_by_field[key] += 1
            nid, title = _null(row.get("id_noticia")), _null(row.get("titulo"))
            if not nid or not title:
                report.exclude(ref, "campo_obligatorio_ausente", "id_noticia o titulo vacío")
                continue
            flags: list[str] = []
            dates = {}
            for key in ("fecha_publicacion", "fecha_deteccion", "fecha_extraccion"):
                dates[key], invalid = _date(row.get(key))
                if invalid:
                    flags.append(f"fecha_invalida:{key}")
            if dates["fecha_extraccion"] is None:
                flags.append("fecha_extraccion_ausente")
            when = dates["fecha_publicacion"] or dates["fecha_deteccion"]
            if when is None:
                flags.append("sin_fecha_util")
            elif not (start <= when < end):
                report.exclude(ref, "fuera_de_intervalo", f"{nid}: {when.isoformat()} fuera de [{start}, {end})")
                continue
            url = _null(row.get("url"))
            norm = _norm_url(url)
            if url and norm is None:
                flags.append("url_invalida")
                url = None
            if norm and norm in seen_urls:
                report.exclude(ref, "url_duplicada", nid)
                continue
            if norm:
                seen_urls.add(norm)
            lang_raw = _null(row.get("idioma"))
            lang = LANG.get(lang_raw.lower(), lang_raw) if lang_raw else None
            if lang_raw and lang != lang_raw:
                flags.append(f"idioma_normalizado:{lang_raw}")
            tema = _null(row.get("tema"))
            try:
                item = NewsItem(
                    id_noticia=nid, titulo=title, url=url, medio=_null(row.get("medio")), idioma=lang,
                    fecha_publicacion=dates["fecha_publicacion"], fecha_deteccion=dates["fecha_deteccion"],
                    fecha_extraccion=dates["fecha_extraccion"] or datetime.now(UTC),
                    tema=Topic(tema) if tema in {t.value for t in Topic} else None,
                    origen=Origin(_null(row.get("origen")) or "gdelt"),
                    alcance_texto=TextScope(_null(row.get("alcance_texto")) or "titular_metadatos"),
                    licencia=_null(row.get("licencia")),
                    sintetico=(_null(row.get("origen")) == Origin.SYNTHETIC.value),
                    quality_flags=flags,
                )
            except ValueError as exc:
                report.exclude(ref, "valor_no_valido", f"{nid}: {exc.__class__.__name__}")
                continue
            for f in flags:
                report.flags[f.split(":")[0]] += 1
            out.append(item)
    report.valid = len(out)
    return out


def load_indicators(path: Path, report: QualityReport) -> list[IndicatorObservation]:
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            value = _null(row.get("valor"))
            extracted, _ = _date(row.get("fecha_extraccion"))
            extra = {k: _null(row[k]) for k in ("periodo", "fuente", "frecuencia") if _null(row.get(k))}
            if _null(row.get("es_proyeccion")):
                extra["es_proyeccion"] = row["es_proyeccion"].strip().lower() in ("true", "1", "si", "sí")
            obs = IndicatorObservation(
                pais_iso3=row["pais_iso3"], indicador_id=row["indicador_id"],
                indicador_nombre=_null(row.get("indicador_nombre")), anio=int(row["anio"]),
                valor=None if value is None else float(value), unidad=_null(row.get("unidad")),
                fuente_url=row["fuente_url"], fecha_extraccion=extracted or datetime.now(UTC),
                licencia=_null(row.get("licencia")), **extra)
            report.indicators += 1
            report.indicators_null_values += obs.valor is None
            out.append(obs)
    return out


def _ms(value) -> datetime | None:
    return None if value is None else datetime.fromtimestamp(value / 1000, tz=UTC)


def load_seismic(path: Path) -> list[SeismicEvent]:
    if not path.exists():
        return []
    events = []
    for f in json.loads(path.read_text(encoding="utf-8")).get("features", []):
        p, coords = f.get("properties", {}), (f.get("geometry") or {}).get("coordinates") or [None, None, None]
        events.append(SeismicEvent(
            id=f["id"], magnitude=p.get("mag"), mag_type=p.get("magType"), time=_ms(p.get("time")),
            updated=_ms(p.get("updated")), longitude=coords[0], latitude=coords[1],
            depth=coords[2] if len(coords) > 2 else None, place=p.get("place"), status=p.get("status"),
            url=p.get("url")))
    return events


def load_snapshot(snapshot: Path) -> tuple[list[NewsItem], list[IndicatorObservation], list[SeismicEvent], dict]:
    snapshot = Path(snapshot)
    report = QualityReport()
    news = load_news(snapshot / "noticias.csv", report)
    indicators = load_indicators(snapshot / "indicadores.csv", report)
    indicators += load_indicators(snapshot / "indicadores_recientes.csv", report)
    official = load_seismic(snapshot / "eventos.geojson")
    extension = load_seismic(snapshot / "eventos_ext.geojson")
    report.seismic_official, report.seismic_extension = len(official), len(extension)
    ids = {q.id for q in official}
    quakes = official + [q for q in extension if q.id not in ids]
    return news, indicators, quakes, report.to_dict()
