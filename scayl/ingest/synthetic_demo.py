"""Replay explicitly invented B-04 cases without adding them to the real corpus."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from scayl.contracts import IndicatorObservation, TextScope, Topic, UIBundle
from scayl.evidence.assemble import build_event
from scayl.ingest.common import json_bytes, utc_now
from scayl.ingest.validate import QualityReport, load_news

CUT = datetime(2026, 10, 1, tzinfo=UTC)


def replay(path: Path) -> tuple[UIBundle, dict]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    all_news, all_indicators, events, results = [], [], [], []
    for case in cases:
        if case.get("sintetico") is not True or case.get("origen") != "sintetico":
            raise ValueError("Every case must be explicitly synthetic")
        for row in case["news"]:
            if (row.get("sintetico") is not True or row.get("origen") != "sintetico"
                    or not row["titulo"].startswith("[SINTÉTICO]")):
                raise ValueError("Every headline must be explicitly synthetic")
        report = QualityReport()
        # This deliberately broad window belongs only to the synthetic replay:
        # T03 predates C-01. Never change the real snapshot's configured window.
        with TemporaryDirectory() as folder:
            csv_path = Path(folder) / "noticias.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(case["news"][0]))
                writer.writeheader()
                writer.writerows(case["news"])
            items = load_news(csv_path, report, (datetime(2024, 1, 1, tzinfo=UTC), CUT))
        # Only authored synthetic descriptions, never RSS bodies. load_news's
        # public adapter omits descriptions; restore these controlled test data.
        by_id = {row["id_noticia"]: row for row in case["news"]}
        items = [item.model_copy(update={
            "descripcion": by_id[item.id_noticia].get("descripcion"),
            "alcance_texto": TextScope(by_id[item.id_noticia]["alcance_texto"]),
        }) for item in items]
        obs = [IndicatorObservation.model_validate(row) for row in case.get("indicators", [])]
        if any(not (row.indicador_nombre or "").startswith("[SINTÉTICO]")
               or "example.invalid" not in row.fuente_url for row in obs):
            raise ValueError("Invented indicator observations must be labelled and use inert URLs")
        event = build_event(case["event_id"], items, Topic(case["topic"]), 1.0, obs, [], CUT)
        all_news.extend(items)
        all_indicators.extend(obs)
        events.append(event)
        results.append({"id": case["id"], "synthetic": True, "quality": report.to_dict(),
                        "evidence_status": event.evidence_status.value,
                        "recirculated": event.is_recirculated,
                        "conflicts": len(event.conflicts), "security_flags": event.security_flags,
                        "publications": event.source_dna.publications,
                        "confirmed_independent": event.source_dna.confirmed_independent})
    bundle = UIBundle(snapshot_version="synthetic-demo", snapshot_cutoff_utc=CUT,
                      signals_total=sum(len(c["news"]) for c in cases), signals_valid=len(all_news),
                      news=all_news, indicators=all_indicators, events=events)
    result = {"run_at": utc_now(), "synthetic": True, "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "cases": results, "scope": "Controlled demonstrations, not real-corpus metrics or human gold"}
    return bundle, result


def main() -> None:
    bundle, report = replay(Path("data/synthetic/cases.jsonl"))
    out = Path("data/processed/synthetic-demo")
    out.mkdir(parents=True, exist_ok=True)
    (out / "bundle.json").write_bytes(json_bytes(bundle.model_dump(mode="json")))
    Path("eval/results/b04-synthetic.json").write_bytes(json_bytes(report))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
