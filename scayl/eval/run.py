"""B-08: reproducible event-level P@5 and saved pytest evidence; never invent measurements."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import xml.etree.ElementTree as ET

from scayl.contracts import UIBundle

ROOT = Path(__file__).resolve().parents[2]
LIMITATION = ("El editor vio antes una propuesta generada por IA, coincidente en 1 de 5 elegidos. "
              "No vio el ranking del sistema ni la app con datos reales. "
              "La selección no es independiente sin asistencia; P@5 es exploratoria (DL-024).")


def unmeasured(reason: str) -> dict:
    return {"status": "no medido", "reason": reason, "num": None, "den": None}


def precision_at_5(bundle: UIBundle, selection: dict) -> dict:
    result = {"value": None, "exploratory": True, "limitation": LIMITATION,
              "prior_ai_proposal_overlap": {"num": 1, "den": 5}, "unit": "eventos"}
    ids = selection.get("ids", [])
    if len(ids) != 5 or len(set(ids)) != 5:
        return {**result, **unmeasured("Se requieren cinco IDs de noticias distintos del editor.")}
    events = sorted(bundle.events, key=lambda e: (-e.priority.score, -e.priority.components.U, e.event_id))
    mapping = {nid: [e.event_id for e in events if nid in e.member_ids] for nid in ids}
    result["news_to_events"] = mapping
    if any(len(mapped) != 1 for mapped in mapping.values()):
        return {**result, **unmeasured("Hay noticias elegidas ausentes o asignadas a más de un evento.")}
    if len(events) < 5 or any(e.synthetic for e in events):
        return {**result, **unmeasured("Se requieren al menos cinco eventos reales, sin casos sintéticos.")}
    chosen = sorted({eid for mapped in mapping.values() for eid in mapped})
    top = [e.event_id for e in events[:5]]
    hits = sorted(set(top) & set(chosen))
    positions = {e.event_id: index + 1 for index, e in enumerate(events)}
    return {**result, "status": "medido", "value": len(hits) / 5, "num": len(hits), "den": 5,
            "editor_event_ids": chosen, "editor_unique_events": len(chosen), "system_top5": top,
            "matched_events": hits, "unmatched_top5": [eid for eid in top if eid not in hits],
            "editor_positions": {eid: positions[eid] for eid in chosen},
            "event_count": len(events), "duplicates_collapsed": 5 - len(chosen),
            "method": "Noticias elegidas → member_ids → eventos únicos; intersección con top 5 / 5. "
                      "Desempate: P descendente, U descendente, event_id ascendente. Sin cambiar pesos."}


def pytest_results(path: Path | None) -> dict:
    results = {f"T{n:02}": {"status": "no medido", "evidence": "Sin ejecución pytest registrada"}
               for n in range(1, 11)}
    if path is None:
        return results
    grouped: dict[str, list[dict]] = {}
    for case in ET.parse(path).iter("testcase"):
        name = f"{case.get('classname')}.{case.get('name')}"
        match = re.search(r"test_t(0[1-9]|10)(?:_|\b)", name.lower())
        tid = f"T{match[1]}" if match else None
        if case.get("name") == "test_pipeline_builds_bundle_and_fichas_offline":
            tid = "T10"
        if tid:
            status = "failed" if case.find("failure") is not None or case.find("error") is not None else (
                "skipped" if case.find("skipped") is not None else "passed")
            grouped.setdefault(tid, []).append({"test": name, "status": status})
    for tid, cases in grouped.items():
        failures = [case for case in cases if case["status"] != "passed"]
        results[tid] = {"status": "passed" if not failures else "failed_or_skipped",
                        "num": len(cases) - len(failures), "den": len(cases),
                        "evidence": str(path), "cases": cases, "failures": failures,
                        "scope": "Pruebas automatizadas; no equivale a validación con LLM real ni ensayo sin wifi."}
    return results


def build_report(bundle: UIBundle, selection: dict, pytest_report: Path | None = None,
                 redteam_report: Path | None = None) -> dict:
    missing = "No hay conjunto etiquetado y ejecución de benchmark guardada para esta métrica."
    metrics = {key: unmeasured(missing) for key in (
        "citation_coverage", "support_validity", "abstention_correct", "abstention_false",
        "topics_macro_f1", "clustering", "tokens", "attribution_preservation")}
    metrics["precision_at_5"] = precision_at_5(bundle, selection)
    redteam = None
    if redteam_report:
        from scayl.eval.redteam import metrics as redteam_metrics

        redteam = json.loads(redteam_report.read_text(encoding="utf-8"))
        rows = redteam["cases"]
        if (redteam.get("schema_version") != 1 or redteam.get("mode") != "template" or not rows
                or len({r["id"] for r in rows}) != len(rows)
                or any(type(r["expected_abstain"]) is not bool
                       or type(r["answer"]["abstained"]) is not bool
                       or r["answer"]["generated_by"]["mode"] != "template" for r in rows)):
            raise ValueError("Reporte red-team inválido o fuera del modo evaluado")
        metrics.update(redteam_metrics(rows))  # recompute num/den from observations, not stored totals
    metrics["latency_ms"] = {key: {"status": "no medido", "median": None, "p95": None, "n": None}
                             for key in ("qa", "package")}
    metrics["api_cost_usd"] = 0.0
    return {"run_at": datetime.now(UTC).isoformat(),
            "snapshot": bundle.snapshot_version,
            "hardware": f"{platform.system()} {platform.machine()} · {platform.processor()} · Python {platform.python_version()}",
            "models": sorted({p.generated_by.model for p in bundle.packages if p.generated_by.model}),
            "generation_modes": sorted({p.generated_by.mode for p in bundle.packages}),
            "metrics": metrics, "tests": pytest_results(pytest_report),
            "cost_scope": "Esta evaluación lee artefactos locales, sin llamadas de API; no mide hardware/electricidad.",
            "redteam": {"evidence": str(redteam_report), "run_at": redteam["run_at"],
                        "failed_ids": redteam["failed_ids"], "scope": redteam["scope"]} if redteam else None,
            "limitations": [LIMITATION, "Solo se miden las métricas con ejecución adjunta; "
                             "generación viva, etiquetas humanas y latencia siguen pendientes."]
                            + (redteam["limitations"] if redteam else [])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default="v1")
    parser.add_argument("--pytest-report", type=Path)
    parser.add_argument("--redteam-report", type=Path, help="Corrida guardada por scayl.eval.redteam")
    args = parser.parse_args()
    bundle_path = ROOT / "data/processed" / args.snapshot / "bundle.json"
    labels_path = ROOT / "data/labels/editor_top5.json"
    bundle = UIBundle.model_validate_json(bundle_path.read_text(encoding="utf-8"))
    selection = json.loads(labels_path.read_text(encoding="utf-8"))
    output = ROOT / "eval/results"
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    saved = output / "runs" / f"{run_id}.json"
    saved.parent.mkdir(parents=True, exist_ok=True)
    pytest_report = None
    if args.pytest_report:
        pytest_report = saved.with_suffix(".pytest.xml")
        shutil.copyfile(args.pytest_report, pytest_report)
    redteam_report = None
    if args.redteam_report:
        redteam_report = saved.with_suffix(".redteam.json")
        shutil.copyfile(args.redteam_report, redteam_report)
    report = build_report(bundle, selection, pytest_report, redteam_report)
    if redteam_report:
        report["redteam"]["evidence"] = redteam_report.relative_to(ROOT).as_posix()
    if pytest_report:
        for test in report["tests"].values():
            if test.get("cases"):
                test["evidence"] = str(pytest_report.relative_to(ROOT))
    paths = [bundle_path, labels_path]
    if pytest_report:
        paths.append(pytest_report)
    if redteam_report:
        paths.append(redteam_report)
    report["inputs"] = [{"path": str(path.relative_to(ROOT) if path.is_absolute() else path),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]
    report["saved_run"] = str(saved.relative_to(ROOT))
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    saved.write_text(payload, encoding="utf-8")
    (output / "latest.json").write_text(payload, encoding="utf-8")
    # Windows consoles may use cp1252; artifacts remain UTF-8, console JSON is portable ASCII.
    print(json.dumps(report["metrics"]["precision_at_5"], ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
