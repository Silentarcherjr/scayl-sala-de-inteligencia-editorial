"""Batch pipeline: frozen snapshot -> data/processed/<snapshot>/bundle.json + fichas.jsonl.

    python -m scayl.pipeline build --snapshot data/raw/v1

Ingestion (B-03), topics and clustering (B-05) are Worker B modules; until they exist the pipeline
uses explicit, labelled fallbacks (topic 'otro', one event per publication) so the flow never breaks.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from scayl.contracts import (
    Event,
    Ficha,
    IndicatorObservation,
    NewsItem,
    ReviewState,
    SeismicEvent,
    StoryPackage,
    Topic,
    UIBundle,
)
from scayl.evidence.assemble import build_event
from scayl.evidence.scoring import rank
from scayl.gen.claims import extract as extract_claims
from scayl.gen.llm import LLM
from scayl.gen.studio import generate_with_report
from scayl.gen.template import build_template_package

log = logging.getLogger("scayl.pipeline")
GENERATION_REPORTS: list[dict] = []  # measured per-package generation facts of the last build (Trust Lab)
ClassifyFn = Callable[[list[NewsItem]], list[tuple[Topic, float | None]]]
ClusterFn = Callable[[list[NewsItem]], list[list[str]]]


def fallback_classify(items: list[NewsItem]) -> list[tuple[Topic, float | None]]:
    log.warning("FALLBACK: topic classifier (B-05) not available; using 'otro'")
    return [(i.tema or Topic.OTRO, None) for i in items]


def fallback_cluster(items: list[NewsItem]) -> list[list[str]]:
    log.warning("FALLBACK: clustering (B-05) not available; one event per publication")
    return [[i.id_noticia] for i in items]


def _majority_topic(labels: list[tuple[Topic, float | None]]) -> tuple[Topic, float | None]:
    counts: dict[Topic, list[float | None]] = {}
    for t, c in labels:
        counts.setdefault(t, []).append(c)
    topic = max(counts, key=lambda t: (len(counts[t]), t != Topic.OTRO))
    confs = [c for c in counts[topic] if c is not None]
    return topic, (sum(confs) / len(confs) if confs else None)


def build_bundle(
    news: list[NewsItem],
    indicators: list[IndicatorObservation],
    quakes: list[SeismicEvent],
    cutoff: datetime,
    snapshot_version: str,
    signals_total: int,
    classify: ClassifyFn = fallback_classify,
    cluster: ClusterFn = fallback_cluster,
    llm: LLM | None = None,
    llm_top_n: int = 15,
    public: bool = False,
) -> UIBundle:
    """``llm`` (live/cache) enriches the top-N events with LLM claims and an LLM Story Studio package;
    other events get the deterministic template. ``public`` strips RSS descriptions (rights)."""
    by_id = {n.id_noticia: n for n in news}
    topics = dict(zip((n.id_noticia for n in news), classify(news)))
    clusters = [c for c in cluster(news) if c]

    def first_date(ids: list[str]):
        dates = [by_id[i].fecha_publicacion or by_id[i].fecha_extraccion for i in ids]
        return min(dates), min(ids)

    events: list[Event] = []
    for n, ids in enumerate(sorted(clusters, key=first_date), start=1):
        items = [by_id[i] for i in ids]
        topic, conf = _majority_topic([topics[i] for i in ids])
        events.append(build_event(f"EVT-{n:04d}", items, topic, conf, indicators, quakes, cutoff))

    events = rank(events)
    if llm is not None and llm.mode != "template":
        enriched = []
        for idx, e in enumerate(events):
            if idx < llm_top_n:
                extra = extract_claims(e, [by_id[i] for i in e.member_ids], llm)
                if extra:
                    gap = e.gap.model_copy(update={"it_is_claimed": e.gap.it_is_claimed + [c.claim_id for c in extra]})
                    e = e.model_copy(update={"claims": e.claims + extra, "gap": gap})
            enriched.append(e)
        events = enriched
    packages, reports = [], []
    for idx, e in enumerate(events):
        if not e.claims:
            continue
        if llm is not None and idx < llm_top_n:
            pkg, report = generate_with_report(e, llm)
            reports.append(report)
        else:
            pkg = build_template_package(e)
        packages.append(pkg)
    GENERATION_REPORTS[:] = reports
    kept_news = [n.model_copy(update={"descripcion": None}) if public else n for n in news]
    return UIBundle(snapshot_version=snapshot_version, snapshot_cutoff_utc=cutoff, signals_total=signals_total,
                    signals_valid=len(news), events=events, packages=packages, news=kept_news,
                    indicators=indicators, seismic=quakes)


def fichas(bundle: UIBundle) -> list[Ficha]:
    pkgs: dict[str, StoryPackage] = {p.event_id: p for p in bundle.packages}
    states: dict[str, ReviewState] = {}
    for r in sorted(bundle.reviews, key=lambda r: r.decided_at):
        states[r.event_id] = r.to_state
    return [
        Ficha(id_caso=e.event_id, ids_fuente=e.member_ids + [r.evidence_id for r in e.official_evidence],
              afirmaciones=e.claims, citas=[r for c in e.claims for r in c.evidence] + e.official_evidence,
              puntaje=e.priority.score, componentes=e.priority.components, estado_evidencia=e.evidence_status,
              borrador=pkgs.get(e.event_id), estado_revision=states.get(e.event_id, ReviewState.NUEVO))
        for e in bundle.events
    ]


def write_outputs(bundle: UIBundle, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "bundle.json").write_text(json.dumps(bundle.model_dump(mode="json"), ensure_ascii=False, indent=1),
                                         encoding="utf-8")
    with (out_dir / "fichas.jsonl").open("w", encoding="utf-8") as f:
        for ficha in fichas(bundle):
            f.write(json.dumps(ficha.model_dump(mode="json"), ensure_ascii=False) + "\n")
    with (out_dir / "generation_report.jsonl").open("w", encoding="utf-8") as f:
        for report in GENERATION_REPORTS:
            f.write(json.dumps(report, ensure_ascii=False) + "\n")


def _load_worker_b(snapshot: Path):
    """Use Worker B modules when present; otherwise fail loudly for ingestion (no fake data)."""
    try:
        from scayl.ingest.validate import load_snapshot  # B-03
    except ImportError as exc:  # pragma: no cover - depends on Worker B progress
        raise SystemExit(f"Ingestion (B-03: scayl.ingest.validate.load_snapshot) not available yet: {exc}")
    news, indicators, quakes, report = load_snapshot(snapshot)
    from scayl.intel import cluster as cluster_mod
    from scayl.intel import topics as topics_mod
    from scayl.intel.embed import get_embedder

    method = os.environ.get("SCAYL_INTEL", "ai" if _ai_available() else "baseline")
    embedder, method = select_embedder(method, get_embedder)
    # Topics and clustering are chosen separately, by measurement (DL-029): on 100 human-labelled C-01
    # headlines the keyword rules beat the E5 prototype classifier (macro-F1 0.76 vs 0.25), while E5 is kept
    # for clustering. SCAYL_TOPICS=ai re-enables the prototype classifier for experiments.
    topics_method = os.environ.get("SCAYL_TOPICS", "baseline")
    log.info("Inteligencia semántica: temas=%s, agrupación=%s", topics_method, embedder.name)

    def classify(items):
        return topics_mod.classify(items, method=topics_method)

    def cluster(items):
        return cluster_mod.cluster(items, embedder)

    write_quality_report(snapshot, report)
    total = getattr(report, "total", None) or (report.get("total") if isinstance(report, dict) else len(news))
    return news, indicators, quakes, classify, cluster, total


def select_embedder(method: str, get_embedder) -> tuple[object, str]:
    """AI embeddings only if the local model actually loads (weights are never downloaded here);
    otherwise the labelled TF-IDF baseline. Missing package -> ImportError; missing weights -> OSError."""
    if method != "ai":
        return get_embedder("tfidf"), "baseline"
    try:
        embedder = get_embedder("st")
        embedder.encode(["prueba de carga del modelo local"])  # loads once; the instance keeps the model
    except Exception as exc:  # noqa: BLE001 - any load failure must degrade, never break the demo
        log.warning("Embeddings IA no disponibles (%s: %s); se usa el baseline TF-IDF", type(exc).__name__, exc)
        return get_embedder("tfidf"), "baseline"
    return embedder, "ai"


def write_quality_report(snapshot: Path, report) -> None:
    """T01 evidence: data/processed/<snap>/quality_report.json (counts, exclusions with reasons, nulls)."""
    out = Path("data/processed") / snapshot.name
    out.mkdir(parents=True, exist_ok=True)
    data = report if isinstance(report, dict) else getattr(report, "to_dict", dict)()
    (out / "quality_report.json").write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str),
                                             encoding="utf-8")


def _ai_available() -> bool:
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def _cutoff(snapshot: Path) -> datetime:
    manifest = snapshot / "manifest.json"
    if manifest.exists():
        raw = json.loads(manifest.read_text(encoding="utf-8")).get("fecha_corte_UTC")
        if raw:
            return datetime.fromisoformat(raw)
    return data_window_cutoff()


def data_window_cutoff() -> datetime:
    """Cutoff from scayl/config/data_window.v1.yaml (organizer clarification C-01, DL-017)."""
    import yaml

    cfg = yaml.safe_load((Path(__file__).parent / "config" / "data_window.v1.yaml").read_text(encoding="utf-8"))
    return datetime.fromisoformat(cfg["cutoff_utc"])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="scayl.pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="snapshot -> bundle.json + fichas.jsonl")
    b.add_argument("--snapshot", type=Path, default=Path("data/raw/v1"))
    b.add_argument("--out", type=Path, default=None)
    b.add_argument("--llm", choices=["template", "live", "cache"], default="template",
                   help="live: Ollama on this machine (fills the cache); cache: reuse precomputed outputs")
    b.add_argument("--top", type=int, default=15, help="events enriched with LLM claims + package")
    b.add_argument("--public", action="store_true", help="strip RSS descriptions (hosted demo)")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    news, indicators, quakes, classify, cluster, total = _load_worker_b(args.snapshot)
    llm = None if args.llm == "template" else LLM(mode=args.llm)
    bundle = build_bundle(news, indicators, quakes, _cutoff(args.snapshot), args.snapshot.name, total,
                          classify, cluster, llm=llm, llm_top_n=args.top, public=args.public)
    out = args.out or Path("data/processed") / args.snapshot.name
    write_outputs(bundle, out)
    log.info("bundle: %d signals -> %d events -> %s", len(news), len(bundle.events), out / "bundle.json")


if __name__ == "__main__":
    main()
