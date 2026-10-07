"""Measured paired evidence comparison with the same news/topics/clusters (B-13/B-14)."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from scayl.ingest.common import json_bytes, utc_now
from scayl.ingest.validate import load_snapshot
from scayl.intel.cluster import cluster
from scayl.intel.embed_st import SentenceTransformerEmbedder
from scayl.intel.topics_ai import classify
from scayl.pipeline import build_bundle


def measure(snapshot: Path = Path("data/raw/v1")) -> dict:
    news, indicators, quakes, report = load_snapshot(snapshot)
    embedder = SentenceTransformerEmbedder()
    topics = classify(news)
    groups = cluster(news, embedder)
    manifest_bytes = (snapshot / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    cutoff = datetime.fromisoformat(manifest["fecha_corte_UTC"])
    common = dict(news=news, quakes=quakes, cutoff=cutoff, snapshot_version=snapshot.name,
                  signals_total=report["total"], classify=lambda _: topics, cluster=lambda _: groups)
    before = build_bundle(indicators=[o for o in indicators if o.fuente == "wb"], **common)
    after = build_bundle(indicators=indicators, **common)
    def counts(bundle):
        c = Counter(e.evidence_status.value for e in bundle.events)
        return {name: c[name] for name in ("suficiente_para_borrador", "parcial", "insuficiente")}
    by_id = {e.event_id: e for e in before.events}
    changed = [{"event_id": e.event_id, "title": e.title,
                "before": by_id[e.event_id].evidence_status.value, "after": e.evidence_status.value,
                "recent_evidence_ids": sorted({r.evidence_id for c in e.claims for r in c.evidence
                                               if r.evidence_id.startswith("ind:")})}
               for e in after.events if e.evidence_status != by_id[e.event_id].evidence_status]
    linked = [{"event_id": e.event_id, "title": e.title,
               "refs": sorted({r.evidence_id for c in e.claims for r in c.evidence
                               if r.evidence_id.startswith("ind:")})}
              for e in after.events if any(r.evidence_id.startswith("ind:")
                                          for c in e.claims for r in c.evidence)]
    result = dict(run_at=utc_now(), cutoff=cutoff.isoformat(), embedder=embedder.name,
                  event_count=len(after.events), before=counts(before), after=counts(after), changes=changed,
                  comparison="Same fixed C-01 news, topic labels, clusters and rules; only ACP/INEC added. Template mode; no LLM.",
                  manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                  parent_manifest=manifest["parent_manifest"],
                  recent_csv_sha256=hashlib.sha256((snapshot / "indicadores_recientes.csv").read_bytes()).hexdigest(),
                  recent_rows=sum(o.fuente != "wb" for o in indicators),
                  recent_nulls=sum(o.fuente != "wb" and o.valor is None for o in indicators),
                  recent_linked_events=linked,
                  limitations=["ACP projections unavailable before cutoff: explicit nulls, never confirmation.",
                               "INEC signed PDF transcription by Codex; human review pending.",
                               "AP-012: generic restriction keyword links ACP context to EVT-0161 (crime). No confirmation; Lead decision pending."])
    Path("eval/results/b13-b14-evidence-before-after.json").write_bytes(json_bytes(result))
    return result


if __name__ == "__main__":
    result = measure()
    print(json.dumps({k: result[k] for k in ("event_count", "before", "after", "recent_rows", "recent_nulls")}, indent=2))
