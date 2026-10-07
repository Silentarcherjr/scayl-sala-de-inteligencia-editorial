"""B-07: assisted annotation forms; metrics only after explicit human labels."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import random

from sklearn.metrics import precision_recall_fscore_support

from scayl.contracts import NewsItem, Topic
from scayl.ingest.common import json_bytes, utc_now, write_csv
from scayl.ingest.validate import load_snapshot
from scayl.intel.cluster import cluster
from scayl.intel.embed import TfidfEmbedder
from scayl.intel.embed_st import SentenceTransformerEmbedder
from scayl.intel.topics import classify

LABELS = Path("data/labels")


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def prepare() -> dict:
    news, _, _, _ = load_snapshot(Path("data/raw/v1"))
    selected = random.Random(20261007).sample(sorted(news, key=lambda x: x.id_noticia), 100)
    predictions = classify(selected, method="ai")
    rows = [{"id_noticia": n.id_noticia, "titulo": n.titulo, "tema_propuesto": t.value,
             "tema_humano": None, "confirmado": None, "revisor": None}
            for n, (t, _) in zip(selected, predictions)]
    write_csv(LABELS / "topics_human.csv", rows,
              ["id_noticia", "titulo", "tema_propuesto", "tema_humano", "confirmado", "revisor"])
    pairs = read_csv(LABELS / "dev2025_cluster_pairs.csv")
    ids = sorted({p[k] for p in pairs for k in ("id_a", "id_b")})
    parents = {key: key for key in ids}
    def find(key):
        while key != parents[key]:
            key = parents[key]
        return key
    for pair in pairs:
        if pair["same_event"] == "1":
            parents[find(pair["id_b"])] = find(pair["id_a"])
    groups = {key: f"G{i + 1:02d}" for i, key in enumerate(sorted({find(k) for k in ids}))}
    dev = {n["id_noticia"]: n for n in (json.loads(line) for line in
            (LABELS / "dev2025_news.jsonl").read_text(encoding="utf-8").splitlines())}
    rows = [{"id_noticia": key, "titulo": dev[key]["titulo"],
             "fecha": dev[key]["fecha_publicacion"] or dev[key]["fecha_deteccion"],
             "grupo_propuesto": groups[find(key)], "grupo_humano": None,
             "confirmado": None, "revisor": None} for key in ids]
    write_csv(LABELS / "dev2025_groups_human.csv", rows,
              ["id_noticia", "titulo", "fecha", "grupo_propuesto", "grupo_humano", "confirmado", "revisor"])
    return {"topic_rows": len(selected), "group_rows": len(rows), "derived_pairs": len(pairs)}


def confirmed(rows: list[dict], field: str) -> list[dict]:
    ready = []
    for row in rows:
        if row.get("confirmado", "").strip().lower() not in {"si", "sí", "true"}:
            continue
        if row.get(field) in (None, "", "null") or row.get("revisor") in (None, "", "null"):
            raise ValueError("Human confirmation needs a label and reviewer")
        ready.append(row)
    if len({r["id_noticia"] for r in ready}) != len(ready):
        raise ValueError("Duplicate reviewed IDs")
    return ready


def evaluate() -> dict:
    topic_rows = confirmed(read_csv(LABELS / "topics_human.csv"), "tema_humano")
    group_rows = confirmed(read_csv(LABELS / "dev2025_groups_human.csv"), "grupo_humano")
    result = {"run_at": utc_now(), "topics": {"status": "no medido; revisión humana pendiente", "n": len(topic_rows)},
              "clustering": {"status": "no medido; revisión humana pendiente", "n_reviewed_headlines": len(group_rows)},
              "limitations": ["Human annotations assisted by model/agent proposals; not blind gold.",
                               "Development clustering pairs were used to calibrate tau on provisional labels; not held-out generalization.",
                               "No tau/prototype/weight tuning in this evaluator; editor_top5 never read."]}
    if len(topic_rows) >= 100:
        news, _, _, _ = load_snapshot(Path("data/raw/v1"))
        lookup = {n.id_noticia: n for n in news}
        items = [lookup[r["id_noticia"]] for r in topic_rows]
        actual = [Topic(r["tema_humano"]).value for r in topic_rows]
        scores = {}
        for method in ("baseline", "ai"):
            predicted = [t.value for t, _ in classify(items, method=method)]
            _, _, f1, _ = precision_recall_fscore_support(actual, predicted,
                labels=[t.value for t in Topic], average="macro", zero_division=0)
            scores[method] = {"macro_f1": float(f1), "n": len(actual)}
        result["topics"] = {"status": "medido", **scores, "macro_scope": "all 7 official classes, zero_division=0"}
    pairs = read_csv(LABELS / "dev2025_cluster_pairs.csv")
    required = {p[k] for p in pairs for k in ("id_a", "id_b")}
    gold = {r["id_noticia"]: r["grupo_humano"] for r in group_rows}
    if required and required <= gold.keys():
        dev = [NewsItem.model_validate(json.loads(line)) for line in
               (LABELS / "dev2025_news.jsonl").read_text(encoding="utf-8").splitlines()]
        methods = {}
        for name, embedder in [("baseline", TfidfEmbedder()), ("ai", SentenceTransformerEmbedder())]:
            membership = {key: i for i, group in enumerate(cluster(dev, embedder)) for key in group}
            tp = fp = fn = tn = 0
            for pair in pairs:
                a, b = pair["id_a"], pair["id_b"]
                actual, predicted = gold[a] == gold[b], membership[a] == membership[b]
                tp += int(actual and predicted)
                fp += int(not actual and predicted)
                fn += int(actual and not predicted)
                tn += int(not actual and not predicted)
            precision = tp / (tp + fp) if tp + fp else 0.0
            recall = tp / (tp + fn) if tp + fn else 0.0
            methods[name] = {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "n_pairs": len(pairs),
                             "precision": {"num": tp, "den": tp + fp, "value": precision},
                             "recall": {"num": tp, "den": tp + fn, "value": recall},
                             "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0}
        result["clustering"] = {"status": "medido; desarrollo asistido", **methods}
    result["labels_sha256"] = {name: hashlib.sha256((LABELS / name).read_bytes()).hexdigest()
        for name in ("topics_human.csv", "dev2025_groups_human.csv")}
    Path("eval/results/b07-human-metrics.json").write_bytes(json_bytes(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "evaluate"])
    print(json.dumps(prepare() if parser.parse_args().command == "prepare" else evaluate(), indent=2))
