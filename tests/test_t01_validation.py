"""T01: invalid dates and nulls are separated without rejecting the whole file."""
from scayl.ingest.validate import QualityReport, load_indicators, load_news
from tests.factories import CUTOFF

HEADER = ("id_noticia,titulo,url,medio,idioma,fecha_publicacion,fecha_deteccion,fecha_extraccion,tema,origen,"
          "alcance_texto,licencia\n")


def test_invalid_dates_nulls_duplicates_and_window(tmp_path):
    rows = [
        "n1,Canal reduce calado,https://a.com/1,a.com,spa,2026-09-20T10:00:00Z,null,2026-10-06T00:00:00Z,null,gdelt,titular_metadatos,null",
        "n2,Fecha rota,https://a.com/2,a.com,es,no-es-fecha,2026-09-21T10:00:00Z,2026-10-06T00:00:00Z,null,gdelt,titular_metadatos,null",
        "n3,,https://a.com/3,a.com,es,2026-09-20T10:00:00Z,null,2026-10-06T00:00:00Z,null,gdelt,titular_metadatos,null",
        "n4,Duplicada,https://www.a.com/1/,a.com,es,2026-09-22T10:00:00Z,null,2026-10-06T00:00:00Z,null,gdelt,titular_metadatos,null",
        "n5,Vieja,https://a.com/5,a.com,es,2024-03-01T10:00:00Z,null,2026-10-06T00:00:00Z,null,tvn_rss,titular_metadatos,null",
    ]
    path = tmp_path / "noticias.csv"
    path.write_text(HEADER + "\n".join(rows) + "\n", encoding="utf-8")
    report = QualityReport()
    news = load_news(path, report)
    assert [n.id_noticia for n in news] == ["n1", "n2"]  # the load continues
    assert news[0].idioma == "es" and news[0].fecha_deteccion is None  # null stays None
    assert news[1].fecha_publicacion is None and "fecha_invalida:fecha_publicacion" in news[1].quality_flags
    assert dict(report.excluded_by_reason) == {"campo_obligatorio_ausente": 1, "url_duplicada": 1,
                                               "fuera_de_intervalo": 1}
    assert report.total == 5 and report.valid == 2


def test_null_indicator_value_is_none_not_zero(tmp_path):
    path = tmp_path / "indicadores.csv"
    path.write_text("pais_iso3,indicador_id,indicador_nombre,anio,valor,unidad,fuente_url,fecha_extraccion,licencia\n"
                    "PAN,SL.UEM.TOTL.ZS,Unemployment,2024,null,%,https://x,2026-10-06T00:00:00Z,CC BY 4.0\n",
                    encoding="utf-8")
    report = QualityReport()
    obs = load_indicators(path, report)
    assert obs[0].valor is None and report.indicators_null_values == 1
    assert CUTOFF  # factories import keeps the synthetic fixtures consistent
