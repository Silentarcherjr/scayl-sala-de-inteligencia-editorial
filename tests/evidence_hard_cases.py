"""[SINTÉTICO] Hard contradiction set (C4). Every record is synthetic (origen=sintetico, sintetico=True) and
written by an AI agent to probe the conflict logic; none of these headlines exists in the real corpus.

Each case: (case_id, category, items, quakes, expected_conflict, rationale). A case is a single event
(publications already clustered together); the detector under test is ``build_event(...).conflicts``.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from tests.factories import news, quake

T = datetime(2025, 9, 29, 12, tzinfo=UTC)
P = "[SINTÉTICO] "


def _n(nid, title, medio, pub=T):
    return news(nid, P + title, medio=medio, pub=pub)


CASES = [
    # --- same fact, different figures -> contradiction --------------------------------------------------
    ("C01", "misma_cifra_distinta", [
        _n("a", "Inflación en Panamá sube a 1,2% en agosto", "x.com"),
        _n("b", "Inflación en Panamá llega a 2,1% en agosto", "y.com")], [], True,
     "Mismo indicador, mismo período y lugar, misma unidad, cifras incompatibles."),
    ("C02", "misma_cifra_distinta", [
        _n("a", "Desempleo en Panamá se ubica en 9,5%", "x.com"),
        _n("b", "Desempleo en Panamá baja a 7,4%", "y.com")], [], True,
     "Mismo indicador sin período explícito en ninguna de las dos versiones."),
    ("C03", "misma_cifra_distinta", [
        _n("a", "Sismo de magnitud 4.5 sacude Chiriquí", "x.com"),
        _n("b", "Sismo de magnitud 5.1 sacude Chiriquí", "y.com")], [], True,
     "Mismo sismo (mismo lugar y hora), magnitudes distintas."),
    # --- different years of the same indicator -> NOT a contradiction ----------------------------------
    ("C04", "distinto_anio", [
        _n("a", "Inflación en Panamá fue de 1,5% en 2023", "x.com"),
        _n("b", "Inflación en Panamá cerró 2024 en 0,7%", "y.com")], [], False,
     "Mismo indicador, años distintos: son dos mediciones, no versiones del mismo dato."),
    ("C05", "distinto_anio", [
        _n("a", "Exportaciones de Panamá crecieron 12% en 2022", "x.com"),
        _n("b", "Exportaciones de Panamá crecen 3% en 2025", "y.com")], [], False,
     "Serie temporal citada en dos notas; distinto período."),
    ("C06", "distinto_periodo", [
        _n("a", "Inflación en Panamá: precios suben 0,4% en julio", "x.com"),
        _n("b", "Inflación en Panamá: precios bajan 0,3% en agosto", "y.com")], [], False,
     "Mismo indicador mensual, meses distintos."),
    # --- different organisations, different magnitudes -------------------------------------------------
    ("C07", "organizaciones_distintas", [
        _n("a", "USGS: sismo de magnitud 4.5 en Chiriquí", "x.com"),
        _n("b", "IGUP reporta sismo de magnitud 4.9 en Chiriquí", "y.com")], [], True,
     "Mismo sismo, dos agencias con cifras distintas: discrepancia que se muestra con atribución."),
    ("C08", "organizaciones_distintas", [
        _n("a", "FMI proyecta que el PIB de Panamá crecerá 3% en 2026", "x.com"),
        _n("b", "PIB de Panamá creció 4,8% en 2026, según el INEC", "y.com")], [], False,
     "Proyección frente a observación: no son versiones del mismo hecho."),
    ("C09", "organizaciones_distintas", [
        _n("a", "Cepal estima que el PIB de Panamá crecerá 3,5% en 2026", "x.com"),
        _n("b", "FMI prevé que el PIB de Panamá crecerá 2,5% en 2026", "y.com")], [], False,
     "Dos proyecciones de organizaciones distintas: pronósticos distintos, no contradicción."),
    # --- corrected versions ----------------------------------------------------------------------------
    ("C10", "correccion", [
        _n("a", "INEC corrige: desempleo en Panamá fue 9,5% y no 9,1%", "x.com")], [], False,
     "Una sola nota que informa una corrección: las dos cifras no son versiones en conflicto entre medios."),
    ("C11", "correccion", [
        _n("a", "Desempleo en Panamá sube a 9,1%", "x.com"),
        _n("b", "INEC corrige: desempleo en Panamá fue 9,5%", "y.com")], [], True,
     ("Versión original y versión corregida en medios distintos: se muestran ambas para que el editor "
      "verifique cuál está vigente.")),
    # --- different events with similar figures -> NOT -------------------------------------------------
    ("C12", "eventos_distintos", [
        _n("a", "Sismo de magnitud 4.5 sacude Chiriquí", "x.com"),
        _n("b", "Sismo de magnitud 4.9 sacude Colón", "y.com", pub=T + timedelta(days=3))], [], False,
     "Dos sismos distintos (lugar y fecha distintos) agrupados juntos: no es contradicción."),
    ("C13", "eventos_distintos", [
        _n("a", "Desempleo en Colón llega a 12%", "x.com"),
        _n("b", "Desempleo en Chiriquí llega a 8%", "y.com")], [], False,
     "Mismo indicador, lugares distintos."),
    ("C14", "eventos_distintos", [
        _n("a", "Inflación en Panamá sube a 1,2%", "x.com"),
        _n("b", "Inflación en Costa Rica sube a 3,4%", "y.com")], [], False,
     "Mismo indicador, países distintos."),
    # --- incompatible units / measures -> NOT a numeric contradiction --------------------------------
    ("C15", "unidades_incompatibles", [
        _n("a", "Exportaciones de Panamá crecen 5%", "x.com"),
        _n("b", "Exportaciones de Panamá crecen 500 millones de dólares", "y.com")], [], False,
     "Porcentaje frente a monto absoluto: no son comparables."),
    ("C16", "unidades_incompatibles", [
        _n("a", "Inflación mensual en Panamá fue 0,2% en julio", "x.com"),
        _n("b", "Inflación interanual en Panamá fue 1,5% en julio", "y.com")], [], False,
     "Variación mensual frente a interanual: medidas distintas."),
    ("C17", "unidades_incompatibles", [
        _n("a", "Precios de la canasta suben 4% y exportaciones caen 9%", "x.com"),
        _n("b", "Precios de la canasta suben 4% en Panamá", "y.com")], [], False,
     "Dos cifras en un titular para dos indicadores distintos: cada cifra va con su indicador."),
    # --- incompatible statements (semantic) ---------------------------------------------------------
    ("C18", "afirmaciones_incompatibles", [
        _n("a", "Sismo sacude la ciudad de Panamá esta madrugada", "x.com"),
        _n("b", "IGUP descarta que se haya registrado un sismo en la ciudad de Panamá", "y.com")], [], True,
     "Una versión afirma el hecho y otra lo descarta."),
    ("C19", "afirmaciones_incompatibles", [
        _n("a", "Canal de Panamá suspende el tránsito por la sequía", "x.com"),
        _n("b", "ACP desmiente que el Canal de Panamá suspenda el tránsito", "y.com")], [], True,
     "Afirmación y desmentido oficial."),
    ("C20", "afirmaciones_incompatibles", [
        _n("a", "IGUP descarta daños tras el sismo en Chiriquí", "x.com"),
        _n("b", "IGUP descarta daños tras el sismo de Chiriquí", "y.com")], [], False,
     "Ambas versiones descartan lo mismo: coinciden."),
    # --- agency duplication -> NOT ------------------------------------------------------------------
    ("C21", "duplicado_agencia", [
        _n("a", "Inflación en Panamá sube a 1,2% en agosto (EFE)", "x.com"),
        _n("b", "Inflación en Panamá sube a 1,2% en agosto (EFE)", "y.com"),
        _n("c", "Inflación en Panamá sube a 1,2% en agosto (EFE)", "z.com")], [], False,
     "Tres réplicas de la misma nota de agencia, misma cifra."),
    ("C22", "duplicado_agencia", [
        _n("a", "Sismo de magnitud 4.6 sacude Chiriquí (EFE)", "x.com"),
        _n("b", "Sismo de 4,6 grados sacude Chiriquí, informa EFE", "y.com")], [], False,
     "Misma cifra con distinta notación decimal."),
    # --- headline vs official source ----------------------------------------------------------------
    ("C23", "titular_vs_oficial", [
        _n("a", "Sismo de magnitud 4.7 sacude Chiriquí", "x.com")],
     [quake("usC23", 4.5, T - timedelta(hours=1))], True,
     "Titular 4.7 frente a USGS 4.5 en la misma ventana: discrepancia visible."),
    ("C24", "titular_vs_oficial", [
        _n("a", "Sismo de magnitud 4.6 sacude Chiriquí", "x.com")],
     [quake("usC24", 4.6, T - timedelta(hours=1))], False,
     "Titular coincide con USGS."),
]

# Written AFTER the improved logic, and never used to change it: a small check against overfitting the
# development cases above. Report it separately; any miss here is reported, not "fixed" silently.
CASES_POSTHOC = [
    ("H01", "misma_cifra_distinta", [
        _n("a", "Exportaciones de Panamá caen 6,5% en el primer semestre", "x.com"),
        _n("b", "Exportaciones de Panamá caen 11% en el primer semestre", "y.com")], [], True,
     "Mismo indicador y período, cifras incompatibles."),
    ("H02", "redondeo", [
        _n("a", "Desempleo en Panamá llega a 9%", "x.com"),
        _n("b", "Desempleo en Panamá llega a 9,4%", "y.com")], [], False,
     "9% es el redondeo de 9,4%: no es contradicción."),
    ("H03", "distinto_anio", [
        _n("a", "Desempleo en Panamá: 7,4% en 2023", "x.com"),
        _n("b", "Desempleo en Panamá: 9,5% en 2024", "y.com")], [], False, "Años distintos."),
    ("H04", "afirmaciones_incompatibles", [
        _n("a", "Gobierno niega cierre de escuelas por lluvias en Darién", "x.com"),
        _n("b", "Cierran escuelas por lluvias en Darién", "y.com")], [], True, "Afirmación frente a negación."),
    ("H05", "afirmaciones_incompatibles", [
        _n("a", "Ministerio niega aumento de tarifa eléctrica", "x.com"),
        _n("b", "Lluvias afectan carreteras en Coclé", "y.com")], [], False,
     "Negación sin relación con la otra nota."),
    ("H06", "organizaciones_distintas", [
        _n("a", "Banco Mundial estima que la economía de Panamá crecerá 3%", "x.com"),
        _n("b", "MEF: el PIB de Panamá creció 2,9%", "y.com")], [], False, "Proyección frente a dato observado."),
    ("H07", "eventos_distintos", [
        _n("a", "Sismo de magnitud 5.0 sacude Costa Rica", "x.com"),
        _n("b", "Sismo de magnitud 4.2 sacude Chiriquí", "y.com")], [], False, "Países distintos."),
    ("H08", "duplicado_agencia", [
        _n("a", "Exportaciones de Panamá suben 4% (AFP)", "x.com"),
        _n("b", "Exportaciones de Panamá suben 4,0% según AFP", "y.com")], [], False, "Misma cifra."),
]


def evaluate(cases=None) -> dict:
    """Run the detector on every case; return per-case outcome + TP/FP/FN/TN, precision and recall."""
    from scayl.contracts import Topic
    from scayl.evidence.assemble import build_event
    from tests.factories import CUTOFF

    rows, tp, fp, fn, tn = [], 0, 0, 0, 0
    for cid, cat, items, quakes, expected, why in (CASES if cases is None else cases):
        topic = Topic.EVENTOS_NATURALES if "ismo" in items[0].titulo else Topic.ECONOMIA
        e = build_event(f"EVT-{cid}", items, topic, 0.9, [], quakes, CUTOFF)
        got = bool(e.conflicts)
        tp, fp = tp + (got and expected), fp + (got and not expected)
        fn, tn = fn + (expected and not got), tn + (not expected and not got)
        rows.append({"case": cid, "category": cat, "expected_conflict": expected, "detected": got,
                     "conflict_fields": [c.field for c in e.conflicts], "rationale": why})
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    return {"n": len(CASES), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": {"num": tp, "den": tp + fp, "value": precision},
            "recall": {"num": tp, "den": tp + fn, "value": recall}, "cases": rows}


if __name__ == "__main__":  # python -m tests.evidence_hard_cases > out.json
    import json
    import sys

    result = {"development": evaluate(), "posthoc": evaluate(CASES_POSTHOC)}
    print(json.dumps(result, ensure_ascii=False, indent=1))
    for name, part in result.items():
        print(name, {k: part[k] for k in ("tp", "fp", "fn", "tn")}, file=sys.stderr)
        for r in part["cases"]:
            if r["expected_conflict"] != r["detected"]:
                print("MISS", r["case"], r["expected_conflict"], r["detected"], r["conflict_fields"], file=sys.stderr)
