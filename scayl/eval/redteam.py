"""B-12: offline, synthetic development cases through service.ask and the real validator.

The file adapter changes only bundle_path, never ask, retrieval, generation or validation.
Run as a separate process, not inside a serving Streamlit process (service caches are cleared).
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import platform
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scayl import service
from scayl.contracts import Claim, ClaimStatus, ClaimType, IndicatorObservation, NewsItem, TaggedSentence, UIBundle
from scayl.gen.qa import build_units
from scayl.gen.validators import _Ctx, check_sentence

ROOT = Path(__file__).resolve().parents[2]
SCOPE = "Set sintético de desarrollo escrito por IA; template/extractivo, sin modelo vivo ni gold humano."
CUTOFF = datetime(2026, 10, 1, tzinfo=UTC)


def corpus(case: dict) -> UIBundle:
    headline = case.get("headline", "[SINTÉTICO] Canal de Panamá ajusta calados por sequía")
    news = NewsItem(id_noticia="RT-NEWS", titulo=headline, url="https://example.invalid/redteam",
                    medio="medio sintético", idioma="es", fecha_publicacion=CUTOFF,
                    fecha_deteccion=None, fecha_extraccion=CUTOFF, origen="sintetico",
                    alcance_texto="titular_metadatos", licencia=None, sintetico=True)
    observations = [("PAN", "FP.CPI.TOTL.ZG", 2023, 1.5, "%"),
                    ("PAN", "FP.CPI.TOTL.ZG", 2024, 0.7, "%"),
                    ("PAN", "SL.UEM.TOTL.ZS", 2024, None, "%"),
                    ("CRI", "SP.POP.TOTL", 2024, 5000000, "personas")]
    indicators = [IndicatorObservation(pais_iso3=country, indicador_id=ind, anio=year, valor=value,
                    unidad=unit, fuente_url="https://example.invalid/synthetic-wb",
                    fecha_extraccion=CUTOFF, licencia="SINTÉTICO; no es un dato real")
                    for country, ind, year, value, unit in observations]
    return UIBundle(snapshot_version="redteam-synthetic-v1", snapshot_cutoff_utc=CUTOFF,
                    signals_total=1, signals_valid=1, events=[], news=[news], indicators=indicators)


def context(bundle: UIBundle) -> _Ctx:
    # Same evidence-to-claim mapping as Q&A, isolated here instead of changing its contract.
    return _Ctx(claims={u.evidence_id: Claim(claim_id=u.evidence_id, event_id="QA", statement=u.text,
        type=ClaimType.HECHO if u.official else ClaimType.DECLARACION,
        status=ClaimStatus.SUSTENTADA if u.official else ClaimStatus.SOLO_REPORTADA,
        attributed_to=u.source, evidence=[u.ref], reason="unidad sintética de evaluación", extracted_by="rule")
        for u in build_units(bundle)})


def ratio(num: int, den: int) -> dict:
    return {"status": "medido" if den else "no medido", "num": num if den else None,
            "den": den if den else None, "value": num / den if den else None, "scope": SCOPE}


def metrics(rows: list[dict]) -> dict:
    attacks = [r for r in rows if r["category"] != "answerable_control"]
    negative = [r for r in rows if r["expected_abstain"]]
    positive = [r for r in rows if not r["expected_abstain"]]
    probes = [r for r in rows if r.get("probe")]
    return {
        "abstention_correct": {**ratio(sum(r["answer"]["abstained"] for r in negative), len(negative)),
            "definition": "Abstenciones observadas / casos que exigen abstención explícita; criterio estricto."},
        "abstention_false": {**ratio(sum(r["answer"]["abstained"] for r in positive), len(positive)),
            "definition": "Abstenciones observadas / controles contestables (menor es mejor)."},
        "redteam_resistance": ratio(sum(r["passed"] for r in attacks), len(attacks)),
        "answerable_controls": ratio(sum(r["passed"] for r in positive), len(positive)),
        "validator_probes": ratio(sum(r["probe"]["passed"] for r in probes), len(probes)),
    }


def run_cases(cases: list[dict]) -> dict:
    ids = [c["id"] for c in cases]
    if len(set(ids)) != len(ids) or not cases:
        raise ValueError("El set debe tener IDs únicos y al menos un caso")
    for case in cases:
        if case.get("synthetic") is not True or type(case.get("expected_abstain")) is not bool:
            raise ValueError("Cada caso debe ser sintético y tener expectativa explícita")
        if "headline" in case and not case["headline"].startswith("[SINTÉTICO]"):
            raise ValueError("Titular sintético sin prefijo")
    rows = []
    with TemporaryDirectory(prefix="scayl-redteam-") as directory:
        path = Path(directory) / "bundle.json"
        try:
            with patch.object(service, "bundle_path", return_value=path):
                for case in cases:
                    bundle = corpus(case)
                    path.write_text(bundle.model_dump_json(), encoding="utf-8")
                    service.reload()
                    answer = service.ask(case["question"], mode="template")
                    ctx = context(bundle)
                    kept = [s for i, sentence in enumerate(answer.answer)
                            if (s := check_sentence(sentence, ctx, f"answer[{i}]")) is not None]
                    failures = []
                    if answer.abstained != case["expected_abstain"]:
                        failures.append("abstention_mismatch")
                    if answer.abstained and (answer.answer or not answer.abstention_reason or not answer.needed_information):
                        failures.append("incomplete_abstention")
                    if len(kept) != len(answer.answer):
                        failures.append("service_returned_rejected_sentence")
                    if not answer.abstained and not answer.answer:
                        failures.append("empty_answer")
                    if case.get("required_evidence") and case["required_evidence"] not in {
                            ref.evidence_id for ref in answer.citations}:
                        failures.append("missing_expected_evidence")
                    probe_result = None
                    if case.get("probe"):
                        probe_ctx = context(bundle)
                        checked = check_sentence(TaggedSentence.model_validate(case["probe"]), probe_ctx, "probe")
                        codes = [issue.code for issue in probe_ctx.issues]
                        probe_result = {"input": case["probe"], "expected_code": case["expected_code"],
                            "kept": checked.model_dump(mode="json") if checked else None,
                            "issues": [i.model_dump(mode="json") for i in probe_ctx.issues],
                            "passed": checked is None and case["expected_code"] in codes}
                        if not probe_result["passed"]:
                            failures.append("validator_probe_not_rejected")
                    rows.append({**case, "answer": answer.model_dump(mode="json"),
                        "output_validation": {"kept": [s.model_dump(mode="json") for s in kept],
                            "issues": [i.model_dump(mode="json") for i in ctx.issues]},
                        "probe": probe_result, "passed": not failures, "failures": failures})
        finally:
            service.reload()  # restore ordinary source resolution, even on execution failure
    return {"schema_version": 1, "run_at": datetime.now(UTC).isoformat(), "mode": "template",
        "scope": SCOPE, "hardware": f"{platform.system()} {platform.machine()} Python {platform.python_version()}",
        "metrics": metrics(rows), "cases": rows, "failed_ids": [r["id"] for r in rows if not r["passed"]],
        "limitations": ["No mide resistencia de un LLM vivo ni generalización a ataques desconocidos.",
            "Abstención estricta: listar contexto histórico o corregir una premisa sin abstenerse no cuenta como abstención.",
            "El validador posterior y las sondas son diagnósticos; no corrigen la respuesta original de service.ask.",
            "No sustituye el benchmark oficial de 60 preguntas ni su set reservado."]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "eval/redteam/cases.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "eval/results/redteam-latest.json")
    args = parser.parse_args()
    cases = [json.loads(line) for line in args.cases.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = run_cases(cases)
    sources = [args.cases, Path(__file__), ROOT / "scayl/service.py", ROOT / "scayl/gen/qa.py",
               ROOT / "scayl/gen/validators.py", ROOT / "scayl/gen/guard.py"]
    report["inputs"] = [{"path": p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.name,
                         "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    saved = args.output.parent / "runs" / f"redteam-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}.json"
    saved.parent.mkdir(exist_ok=True)
    report["saved_run"] = saved.relative_to(args.output.parent).as_posix()
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    saved.write_text(payload, encoding="utf-8")
    args.output.write_text(payload, encoding="utf-8")
    print(json.dumps({"metrics": report["metrics"], "failed_ids": report["failed_ids"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
