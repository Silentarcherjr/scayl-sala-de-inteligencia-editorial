"""Builders for synthetic test records (all marked synthetic)."""
from datetime import UTC, datetime

from scayl.contracts import IndicatorObservation, NewsItem, Origin, SeismicEvent, TextScope

CUTOFF = datetime(2025, 10, 1, tzinfo=UTC)


def news(nid, titulo, medio="medio-a.com", pub=datetime(2025, 9, 29, 12, tzinfo=UTC), det=None, **kw):
    return NewsItem(id_noticia=nid, titulo=titulo, url=f"https://{medio}/{nid}", medio=medio, idioma="es",
                    fecha_publicacion=pub, fecha_deteccion=det or pub, fecha_extraccion=CUTOFF, tema=None,
                    origen=kw.pop("origen", Origin.SYNTHETIC), alcance_texto=TextScope.TITULAR_METADATOS,
                    licencia=None, sintetico=True, **kw)


def wb(ind, year, value, country="PAN", unit="%"):
    return IndicatorObservation(pais_iso3=country, indicador_id=ind, indicador_nombre=ind, anio=year, valor=value,
                                unidad=unit, fuente_url=f"https://data.worldbank.org/indicator/{ind}",
                                fecha_extraccion=CUTOFF, licencia="CC BY 4.0")


def quake(qid, mag, when, place="10 km S of Boquete, Panama"):
    return SeismicEvent(id=qid, magnitude=mag, time=when, updated=when, longitude=-82.4, latitude=8.6, depth=10.0,
                        place=place, status="reviewed", url=f"https://earthquake.usgs.gov/earthquakes/eventpage/{qid}")


def recent(series, periodo, value, fuente, unit, proj=False):
    from scayl.contracts import IndicatorObservation
    freq = "diaria" if len(periodo) == 10 else "mensual"
    return IndicatorObservation(pais_iso3="PAN", indicador_id=series, indicador_nombre=series, anio=int(periodo[:4]),
                                valor=value, unidad=unit, fuente_url=f"https://example.invalid/{fuente}",
                                fecha_extraccion=CUTOFF, licencia="pública", periodo=periodo, fuente=fuente,
                                frecuencia=freq, es_proyeccion=proj)
