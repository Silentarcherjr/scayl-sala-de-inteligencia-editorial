"""Export the reviewed offline demo through scayl.service; no live inference.

Template answer timestamps use the snapshot cutoff for reproducible artifacts.
Existing processed data and the caller's environment are restored after prepare().
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deploy.prepare import check_public
from scayl import service
from scripts.demo_offline import ROOT, prepare


def constants(path: Path, names: set[str]) -> dict:
    result = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    result[target.id] = ast.literal_eval(node.value)
    return result


def export(out: Path) -> None:
    target = ROOT / "data/processed/v1/bundle.json"
    previous = target.read_bytes() if target.exists() else None
    old_env = dict(os.environ)
    try:
        os.environ.update(prepare())
        service.reload()
        bundle = service.load_bundle()
        check_public(bundle.model_dump(mode="json"))
        weights = service.official_weights()
        events = sorted(bundle.events, key=lambda e: (-e.priority.score, -e.priority.components.U, e.event_id))
        news = {n.id_noticia: n for n in bundle.news}
        payloads = {}
        payloads["meta.json"] = {
            "snapshot_version": bundle.snapshot_version,
            "snapshot_cutoff_utc": bundle.snapshot_cutoff_utc.isoformat(),
            "signals_total": bundle.signals_total, "signals_valid": bundle.signals_valid,
            "events_total": len(events), "weights": weights,
            "exported_at": datetime.now(UTC).isoformat(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        }
        summaries = []
        for event in events:
            data = event.model_dump(mode="json")
            package = service.get_package(event.event_id)
            summary = {key: data[key] for key in (
                "event_id", "title", "topic", "priority", "evidence_status", "recommended_action",
                "last_published", "first_detected", "is_recirculated", "synthetic")}
            summary["source_dna"] = {k: data["source_dna"][k] for k in (
                "publications", "max_possible_independent", "confirmed_independent")}
            summary["has_conflicts"] = bool(event.conflicts)
            summary["package_mode"] = package.generated_by.mode if package else None
            # All official score contributions and agenda reasons are calculated in Python.
            summary["contributions"] = {k: weights[k] * getattr(event.priority.components, k) for k in weights}
            keys = sorted(("R", "I", "U", "N", "E"), key=lambda k: -summary["contributions"][k])[:2]
            summary["top_reasons"] = [{"key": k, "reason": event.priority.components.rationale[k]} for k in keys]
            summaries.append(summary)
            data["contributions"] = summary["contributions"]
            data["headlines"] = [
                {k: news[nid].model_dump(mode="json")[k] for k in (
                    "id_noticia", "titulo", "medio", "url", "idioma", "fecha_publicacion", "origen")}
                for nid in event.member_ids
            ]
            data["package"] = package.model_dump(mode="json") if package else None
            payloads[f"cases/{event.event_id}.json"] = data
        payloads["events.json"] = summaries
        source = constants(ROOT / "app/pages/2_Consultas.py", {"EXAMPLES", "JURY"})
        answers = []
        for label, question in source["EXAMPLES"].items():
            answer = service.ask(question, mode="cache").model_dump(mode="json")
            if answer["generated_by"]["mode"] == "template":
                answer["generated_by"]["created_at"] = bundle.snapshot_cutoff_utc.isoformat()
            answers.append({"label": label, "question": question, "answer": answer})
        ordered = sorted(events, key=lambda e: e.event_id)
        jury = []
        for index, label in enumerate(source["JURY"]):
            event = None
            if index == 0:
                event = next((e for e in ordered if e.official_evidence), None)
            elif index == 1:
                event = next((e for e in ordered if any(
                    g.label.value == "procedencia_comun_identificada" for g in e.source_dna.groups)), None)
            elif index == 3:
                event = next((e for e in ordered if e.security_flags), None)
            jury.append({"label": label, "question": label, "event_id": event.event_id if event else None,
                         "evidence": [r.model_dump(mode="json") for r in event.official_evidence]
                         if event and index == 0 else [],
                         "statement": event.source_dna.statement if event and index == 1 else None,
                         "publications": event.source_dna.publications if event else None,
                         "confirmed_independent": event.source_dna.confirmed_independent if event else None,
                         "synthetic": event.synthetic if event else False,
                         "title": event.title if event else None,
                         "answer": answers[2]["answer"] if index == 2 else None})
        payloads["qa.json"] = {"examples": answers, "jury": jury}
        payloads["trust_lab.json"] = {"lab": service.trust_lab(), "generation": service.generation_summary(),
                                     "test_definitions": constants(ROOT / "app/pages/3_Trust_Lab.py", {"TESTS"})["TESTS"]}
        payloads["bulletins.json"] = [service.sector_bulletin(sector).model_dump(mode="json")
                                      for sector in ("logistica_canal", "economia")]
        # Validate everything before writing anything, including model output citations.
        check_public(payloads)
        for relative, value in sorted(payloads.items()):
            path = out / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    finally:
        if previous is None:
            target.unlink(missing_ok=True)
        else:
            target.write_bytes(previous)
        os.environ.clear()
        os.environ.update(old_env)
        service.reload()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "web/public/data")
    export(parser.parse_args().out)
