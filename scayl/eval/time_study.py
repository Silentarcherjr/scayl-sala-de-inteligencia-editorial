"""H-06: summarize three human timed pairs without inventing missing durations."""
import argparse
import csv
import hashlib
import json
import math
import statistics
from datetime import UTC, datetime
from pathlib import Path


def summarize(path: Path) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 3 or {r["task_id"] for r in rows} != {"H06-1", "H06-2", "H06-3"}:
        raise ValueError("Se requieren exactamente las tres tareas H06-1/2/3")
    measured = []
    for row in rows:
        for field in ("manual_seconds", "assisted_seconds"):
            if row[field].strip():
                seconds = float(row[field])
                if not math.isfinite(seconds) or seconds <= 0:
                    raise ValueError("Duraciones medidas positivas y finitas, en segundos")
        if all(row[k].strip() for k in ("participant", "order", "manual_seconds", "assisted_seconds",
                                       "completed_at_utc", "manual_output", "assisted_output")):
            at = datetime.fromisoformat(row["completed_at_utc"])
            if at.utcoffset() is None or at.utcoffset().total_seconds() != 0:
                raise ValueError("Registrar fecha UTC")
            if row["order"] not in {"manual-asistido", "asistido-manual"}:
                raise ValueError("Orden de ejecución inválido")
            measured.append({**row, "manual_seconds": float(row["manual_seconds"]),
                             "assisted_seconds": float(row["assisted_seconds"])})
    complete = len(measured) == 3
    manual = sum(r["manual_seconds"] for r in measured) if complete else None
    assisted = sum(r["assisted_seconds"] for r in measured) if complete else None
    return {"run_at": datetime.now(UTC).isoformat(), "status": "medido" if complete else "no medido",
            "n": len(measured), "planned_n": 3, "exploratory": True, "evidence": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "pairs": measured,
            "manual_seconds_total": manual, "assisted_seconds_total": assisted,
            "difference_seconds": manual - assisted if complete else None,
            "relative_difference": {"num": manual - assisted if complete else None, "den": manual,
                                    "value": (manual - assisted) / manual if complete else None},
            "median_pair_difference_seconds": statistics.median(r["manual_seconds"] - r["assisted_seconds"]
                for r in measured) if complete else None,
            "limitations": ["Tres pares exploratorios, no evidencia causal ni generalizable de ahorro.",
                "Tiempos humanos autorreportados; comparar resultados y condiciones, registrar familiaridad/orden.",
                "No afirmar ahorro si faltan tiempos/resultados o si la calidad de las tareas no es comparable."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/labels/time_study.csv"))
    parser.add_argument("--output", type=Path, default=Path("eval/results/time-study.json"))
    args = parser.parse_args()
    result = summarize(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True))
