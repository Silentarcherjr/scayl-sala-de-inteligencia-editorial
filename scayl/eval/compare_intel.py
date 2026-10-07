"""Post-calibration C-01 comparison. Editor selections are evaluation only."""
from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from scayl.ingest.validate import load_snapshot
from scayl.intel.cluster import DEFAULT_TAU, MAX_GAP, _when, cluster
from scayl.intel.embed import TfidfEmbedder
from scayl.intel.embed_st import SentenceTransformerEmbedder
from scayl.intel.topics import classify
from scayl.intel.topics_ai import classify as classify_ai
from scayl.pipeline import build_bundle


def target_pairs(news, vectors, targets, tau):
    lookup = {item.id_noticia: index for index, item in enumerate(news)}
    names = list(targets)
    result = []
    for a, left in enumerate(names):
        for right in names[a + 1:]:
            i, j = lookup[targets[left][0]], lookup[targets[right][0]]
            gap = abs(_when(news[i]) - _when(news[j]))
            result.append({"left": left, "right": right,
                           "gap_days": gap.total_seconds() / 86400,
                           "blocked_by_7_day_rule": gap > MAX_GAP,
                           "cosine": float(vectors[i] @ vectors[j]),
                           "tau": tau})
    return result


def compare(snapshot: Path = Path("data/raw/v1")) -> dict:
    calibration_path = Path("eval/results/b05-dev2025-calibration.json")
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    ai = SentenceTransformerEmbedder()
    if DEFAULT_TAU[ai.name] != calibration["selected"]["tau"]:
        raise ValueError("Default threshold must match frozen development calibration")
    news, indicators, quakes, quality = load_snapshot(snapshot)
    manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
    cutoff = datetime.fromisoformat(manifest["fecha_corte_UTC"])
    baseline = build_bundle(news, indicators, quakes, cutoff, snapshot.name, quality["total"],
        classify=lambda items: classify(items, method="baseline"),
        cluster=lambda items: cluster(items, TfidfEmbedder()))
    started = time.perf_counter()
    texts = [" ".join(filter(None, (item.titulo, item.descripcion))) for item in news]
    vectors = ai.encode(texts)
    embedding_seconds = time.perf_counter() - started

    class Precomputed:
        name = ai.name

        def encode(self, batch: list[str]) -> np.ndarray:
            if batch != texts:
                raise ValueError("Evaluation text order changed")
            return vectors

    output = Path("data/processed") / snapshot.name
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output / "embeddings.npz", vectors=vectors,
        ids=np.array([item.id_noticia for item in news]), model=np.array(ai.name),
        text_sha256=np.array([hashlib.sha256(text.encode()).hexdigest() for text in texts]))
    after = build_bundle(news, indicators, quakes, cutoff, snapshot.name, quality["total"],
                         classify=classify_ai, cluster=lambda items: cluster(items, Precomputed()))
    # Read the editor reference only AFTER calibration and both bundles are fixed.
    chosen = set(json.loads(Path("data/labels/editor_top5.json").read_text(encoding="utf-8-sig"))["ids"])

    def metrics(bundle):
        top = bundle.events[:5]
        hits = sum(bool(chosen.intersection(event.member_ids)) for event in top)
        coverage = len(chosen.intersection({key for event in top for key in event.member_ids}))
        return {"event_count": len(bundle.events),
                "p_at_5": {"num": hits, "den": 5, "value": hits / 5},
                "selected_headline_coverage_at_5": {"num": coverage, "den": len(chosen)},
                "top5_event_ids": [event.event_id for event in top]}

    target_ids = ("EVT-0088", "EVT-0127", "EVT-0158", "EVT-0096")
    targets = {event.event_id: event.member_ids for event in baseline.events if event.event_id in target_ids}
    if set(targets) != set(target_ids):
        raise ValueError("Requested baseline events not found; inspect snapshot version")
    diagnostic = {}
    group_ids = set()
    for old_id, members in targets.items():
        matches = [event.event_id for event in after.events if set(members).intersection(event.member_ids)]
        group_ids.update(matches)
        diagnostic[old_id] = {"member_ids": members, "after_event_ids": matches}
    result = {"at": datetime.now(UTC).isoformat(), "snapshot": snapshot.name,
              "manifest_sha256": hashlib.sha256((snapshot / "manifest.json").read_bytes()).hexdigest(),
              "calibration_sha256": hashlib.sha256(calibration_path.read_bytes()).hexdigest(),
              "model": ai.name, "tau": DEFAULT_TAU[ai.name], "device": ai.device,
              "embedding_seconds": embedding_seconds, "before": metrics(baseline), "after": metrics(after),
              "requested_four": diagnostic, "four_in_one_event": len(group_ids) == 1,
              "requested_pair_diagnostics": target_pairs(news, vectors, targets, DEFAULT_TAU[ai.name]),
              "evaluation_notes": [
                  "P@5 is an exploratory observation, never a calibration objective.",
                  "P@5 counts top-five event slots overlapping editor headlines; headline coverage is separate because several selections may collapse into one event.",
                  "Editor saw an AI suggestion before selecting; assistance disclosed in DL-024.",
                  "No ACP/INEC added; prototype cosine is not calibrated truth or evidence confidence.",
                  "Development labels are provisional agent annotations; human B-07 validation pending."]}
    path = Path("eval/results/b05-c01-before-after.json")
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("before", "after", "four_in_one_event")}, indent=2))
    return result


if __name__ == "__main__":
    compare()
