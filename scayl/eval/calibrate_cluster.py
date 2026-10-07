"""Calibrate only on labelled 2025 development pairs; never read editor selections."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from scayl.contracts import NewsItem
from scayl.intel.cluster import cluster
from scayl.intel.embed_st import SentenceTransformerEmbedder


def calibrate(news_path: Path, pairs_path: Path, output: Path) -> dict:
    all_items = {item.id_noticia: item for item in
                 (NewsItem.model_validate_json(line) for line in news_path.read_text(encoding="utf-8").splitlines())}
    with pairs_path.open(encoding="utf-8", newline="") as handle:
        pairs = list(csv.DictReader(handle))
    ids = sorted({row[key] for row in pairs for key in ("id_a", "id_b")})
    items = [all_items[key] for key in ids]
    for item in items:
        when = item.fecha_publicacion or item.fecha_deteccion
        if when is None or when.year != 2025 or when >= datetime(2025, 10, 2, tzinfo=UTC):
            raise ValueError("Calibration accepts only pre-C-01 2025 development news")
    embedder = SentenceTransformerEmbedder()
    texts = [" ".join(filter(None, (item.titulo, item.descripcion))) for item in items]
    vectors = embedder.encode(texts)

    class Precomputed:
        name = embedder.name

        def encode(self, batch: list[str]) -> np.ndarray:
            if batch != texts:
                raise ValueError("Calibration text order changed")
            return vectors

    grid = []
    for tau in np.arange(0.70, 0.951, 0.01):
        tau = round(float(tau), 2)
        groups = cluster(items, Precomputed(), tau=tau)
        membership = {key: index for index, group in enumerate(groups) for key in group}
        tp = fp = fn = tn = 0
        for pair in pairs:
            predicted = membership[pair["id_a"]] == membership[pair["id_b"]]
            actual = bool(int(pair["same_event"]))
            tp += int(predicted and actual)
            fp += int(predicted and not actual)
            fn += int(not predicted and actual)
            tn += int(not predicted and not actual)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
        grid.append({"tau": tau, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                     "precision": precision, "recall_on_labelled_dev_pairs": recall, "f1": f1})
    best = max(grid, key=lambda row: (row["f1"], row["precision"], row["tau"]))
    result = {"at": datetime.now(UTC).isoformat(), "model": embedder.name,
              "device": embedder.device, "news_count": len(items), "pair_count": len(pairs),
              "labelers": sorted({p["labeler"] for p in pairs}),
              "limitations": "Provisional agent annotations; not human gold or held-out evaluation. B-07 human review pending.",
              "news_sha256": hashlib.sha256(news_path.read_bytes()).hexdigest(),
              "pairs_sha256": hashlib.sha256(pairs_path.read_bytes()).hexdigest(),
              "selection_rule": "max development pair F1, then precision, then stricter tau; no editor/C-01 inputs",
              "selected": best, "grid": grid}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(best))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--news", type=Path, default=Path("data/labels/dev2025_news.jsonl"))
    parser.add_argument("--pairs", type=Path, default=Path("data/labels/dev2025_cluster_pairs.csv"))
    parser.add_argument("--output", type=Path, default=Path("eval/results/b05-dev2025-calibration.json"))
    args = parser.parse_args()
    calibrate(args.news, args.pairs, args.output)
