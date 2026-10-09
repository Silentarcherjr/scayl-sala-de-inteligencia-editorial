"""QA benchmark v2 over the demo corpus (Subagente B).

Runs the real ``qa.answer`` in template/extractive mode (no LLM) over ``data/labels/qa_benchmark_v2.jsonl``
and the public demo bundle. Measures, per retriever and split:

- retrieval: Hit@5 and recall@5 against ``expected_evidence_ids`` (answerable + contradiction items),
  both-sides coverage for contradictions;
- behaviour: correct abstention, wrong abstention (abstained though answerable), answered-when-should-abstain,
  reason-class agreement, injection/instruction leaks, answers without citations;
- latency p50/p95 of the full ``answer`` call (ms, this machine).

Held-out discipline: the default is ``--splits dev``. The held-out split is evaluated once, at the end.
E5 is used only if its weights are already cached locally (no downloads); otherwise it is reported as
"no medido". Labels were written by an AI agent without human review; scores are not human gold.

    python -m scayl.eval.qa_benchmark --splits dev --label after --output eval/results/b-qa-dev.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import statistics
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

from scayl.contracts import UIBundle
from scayl.gen.llm import LLM

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "data" / "labels" / "qa_benchmark_v2.jsonl"
BUNDLE = ROOT / "deploy" / "artifacts" / "v1" / "bundle.public.json"
K = 5

# Abstention reason text -> class. Classes are the benchmark vocabulary, matched on the reason the user sees.
REASON_PATTERNS = [
    ("suspicious_input", r"la pregunta contiene instrucciones"),
    ("suspicious_source", r"instrucciones sospechosas|posible inyecci"),
    ("null_value", r"nulo|vac[ií]o"),
    ("false_premise", r"cifra planteada"),
    ("historical_only", r"hist[oó]rica"),
    ("period_not_covered", r"per[ií]odo solicitado"),
    ("irrelevant", r"no responde|no contesta|no trata"),
    ("no_evidence", r"no contiene evidencia|no hay evidencia"),
    ("validation_failed", r"validaci[oó]n|no pudo sustentarse"),
]
COMPATIBLE = {"irrelevant": {"irrelevant", "no_evidence"}, "no_evidence": {"no_evidence", "irrelevant"}}


def reason_class(reason: str | None) -> str:
    text = (reason or "").lower()
    for name, pattern in REASON_PATTERNS:
        if re.search(pattern, text):
            return name
    return "other"


def load_items(path: Path = BENCH, splits: tuple[str, ...] = ("dev",)) -> list[dict]:
    items = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [i for i in items if i["split"] in splits]


def load_qa(path: str | None) -> ModuleType:
    if not path:
        from scayl.gen import qa
        return qa
    spec = importlib.util.spec_from_file_location("qa_alt", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def e5_available() -> tuple[bool, str]:
    """True only if sentence-transformers is importable AND the E5 weights are in the local HF cache."""
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        return False, "sentence-transformers no instalado"
    hub = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
    if not any(hub.glob("models--intfloat--multilingual-e5-*")):
        return False, f"pesos E5 no presentes en {hub}"
    return True, "disponible localmente"


def _pct(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, round(q * (len(ordered) - 1)))], 2)


def answer_text(a) -> str:
    return " ".join(s.text for s in a.answer)


def evaluate(items: list[dict], qa: ModuleType, bundle: UIBundle, retriever) -> dict:
    llm = LLM(mode="template")
    rows = []
    for item in items:
        expected = item.get("expected_evidence_ids") or []
        query = qa.normalize_dates(item["question"])
        top = [u.evidence_id for u, _ in retriever.search(query, k=K)]
        start = time.perf_counter()
        a = qa.answer(item["question"], bundle, llm, retriever=retriever)
        ms = (time.perf_counter() - start) * 1000
        cited = [c.evidence_id for c in a.citations]
        text = answer_text(a).lower()
        leak_hits = [m for m in item.get("leak_markers", []) if m.lower() in text]
        row = {"id": item["id"], "split": item["split"], "category": item["category"],
               "expected_behavior": item["expected_behavior"], "abstained": a.abstained,
               "reason_class": reason_class(a.abstention_reason) if a.abstained else None,
               "top5": top, "cited": cited, "latency_ms": round(ms, 2),
               "leak": bool(not a.abstained and (leak_hits or not cited)), "leak_markers_found": leak_hits}
        if expected:
            row["hit5"] = any(e in top for e in expected)
            row["recall5"] = sum(e in top for e in expected) / len(expected)
            row["cited_expected"] = any(e in cited for e in expected)
        if item.get("sides"):
            row["sides_in_top5"] = all(any(e in top for e in side) for side in item["sides"])
            row["sides_cited"] = all(any(e in cited for e in side) for side in item["sides"])
        if item["expected_behavior"] == "abstain":
            exp = item.get("expected_reason_class")
            row["reason_match"] = bool(a.abstained and row["reason_class"] in COMPATIBLE.get(exp, {exp}))
        rows.append(row)
    return {"summary": summarize(rows), "items": rows}


def _frac(rows: list[dict], key, pred) -> dict:
    pool = [r for r in rows if pred(r)]
    num = sum(1 for r in pool if key(r))
    return {"num": num, "den": len(pool), "rate": round(num / len(pool), 3) if pool else None}


def summarize(rows: list[dict]) -> dict:
    def answerable(r):
        return r["expected_behavior"] == "answer"

    def should_abstain(r):
        return r["expected_behavior"] == "abstain"

    with_evidence = [r for r in rows if "hit5" in r]
    return {
        "n": len(rows),
        "hit_at_5": _frac(with_evidence, lambda r: r["hit5"], lambda r: True),
        "recall_at_5_mean": round(statistics.mean(r["recall5"] for r in with_evidence), 3) if with_evidence else None,
        "answered_with_expected_citation": _frac(rows, lambda r: not r["abstained"] and r["cited_expected"],
                                                 answerable),
        "contradiction_both_sides_top5": _frac(rows, lambda r: r["sides_in_top5"], lambda r: "sides_in_top5" in r),
        "contradiction_both_sides_cited": _frac(rows, lambda r: r["sides_cited"], lambda r: "sides_cited" in r),
        "correct_abstention": _frac(rows, lambda r: r["abstained"], should_abstain),
        "reason_class_match": _frac(rows, lambda r: r["reason_match"], should_abstain),
        "wrong_abstention": _frac(rows, lambda r: r["abstained"], answerable),
        "answered_when_should_abstain": _frac(rows, lambda r: not r["abstained"], should_abstain),
        "injection_or_instruction_leaks": _frac(rows, lambda r: r["leak"], lambda r: r["category"] == "adversarial"),
        "leaks_all_items": _frac(rows, lambda r: r["leak"], lambda r: True),
        "latency_ms_p50": _pct([r["latency_ms"] for r in rows], .5),
        "latency_ms_p95": _pct([r["latency_ms"] for r in rows], .95),
    }


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"


def run(splits: tuple[str, ...], label: str, qa_path: str | None, bundle_path: Path, bench: Path,
        with_tfidf_hybrid: bool = True) -> dict:
    qa = load_qa(qa_path)
    bundle = UIBundle.model_validate(json.loads(bundle_path.read_text(encoding="utf-8")))
    items = load_items(bench, splits)
    units = qa.build_units(bundle)
    retrievers: dict[str, object] = {"bm25": qa.Retriever(units)}
    ok, why = e5_available()
    results: dict[str, object] = {}
    if with_tfidf_hybrid:
        from scayl.intel.embed import TfidfEmbedder
        from scayl.intel.retrieve import HybridQARetriever
        retrievers["hybrid_bm25_tfidfchar_rrf"] = HybridQARetriever(units, TfidfEmbedder(), qa_module=qa)
    if ok:
        from scayl.intel.embed import get_embedder
        from scayl.intel.retrieve import DenseQARetriever, HybridQARetriever
        emb = get_embedder("st")
        retrievers["e5"] = DenseQARetriever(units, emb, qa_module=qa)
        retrievers["hybrid_bm25_e5_rrf"] = HybridQARetriever(units, emb, qa_module=qa)
    else:
        results["e5"] = f"no medido ({why})"
        results["hybrid_bm25_e5_rrf"] = f"no medido ({why})"
    for name, retriever in retrievers.items():
        results[name] = {split: evaluate([i for i in items if i["split"] == split], qa, bundle, retriever)
                         for split in splits}
    return {
        "label": label,
        "commit": _commit(),
        "qa_module": qa_path or "scayl/gen/qa.py (HEAD)",
        "date": datetime.now(UTC).isoformat(timespec="seconds"),
        "hardware": {"platform": platform.platform(), "machine": platform.machine(),
                     "processor": platform.processor() or "desconocido", "cpu_count": os.cpu_count(),
                     "python": platform.python_version()},
        "mode": "template (extractivo, sin LLM)",
        "corpus": {"path": str(bundle_path.relative_to(ROOT)) if bundle_path.is_relative_to(ROOT) else str(bundle_path),
                   "sha256": _sha(bundle_path), "units": len(units)},
        "benchmark": {"path": str(bench.relative_to(ROOT)) if bench.is_relative_to(ROOT) else str(bench),
                      "sha256": _sha(bench), "splits": list(splits), "n": len(items),
                      "author": "IA (Subagente B), sin revisión humana"},
        "scope": ("Etiquetas escritas por IA sin revisión humana; no es gold humano ni el set reservado del jurado. "
                  "Latencias de esta máquina, modo extractivo; no miden un LLM."),
        "retrievers": results,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--splits", default="dev", help="coma: dev,heldout")
    p.add_argument("--label", default="run")
    p.add_argument("--qa-module", default=None, help="ruta a una versión alternativa de qa.py (p. ej. baseline)")
    p.add_argument("--bundle", type=Path, default=BUNDLE)
    p.add_argument("--bench", type=Path, default=BENCH)
    p.add_argument("--no-tfidf-hybrid", action="store_true")
    p.add_argument("--output", type=Path, default=ROOT / "eval" / "results" / "b-qa-benchmark.json")
    a = p.parse_args()
    report = run(tuple(s.strip() for s in a.splits.split(",") if s.strip()), a.label, a.qa_module,
                 a.bundle.resolve(), a.bench.resolve(), not a.no_tfidf_hybrid)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for name, res in report["retrievers"].items():
        if isinstance(res, str):
            print(f"{name}: {res}")
            continue
        for split, r in res.items():
            s = r["summary"]
            print(f"{name}/{split}: hit@5 {s['hit_at_5']['num']}/{s['hit_at_5']['den']} "
                  f"answered+cited {s['answered_with_expected_citation']['num']}/"
                  f"{s['answered_with_expected_citation']['den']} "
                  f"correct_abst {s['correct_abstention']['num']}/{s['correct_abstention']['den']} "
                  f"reason {s['reason_class_match']['num']}/{s['reason_class_match']['den']} "
                  f"wrong_abst {s['wrong_abstention']['num']}/{s['wrong_abstention']['den']} "
                  f"leaks {s['injection_or_instruction_leaks']['num']}/{s['injection_or_instruction_leaks']['den']} "
                  f"sides_top5 {s['contradiction_both_sides_top5']['num']}/{s['contradiction_both_sides_top5']['den']} "
                  f"p50 {s['latency_ms_p50']}ms p95 {s['latency_ms_p95']}ms")


if __name__ == "__main__":
    main()
