"""B-09: export reproducible claim/evidence rows; only a human supplies support labels."""
from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path

from scayl.contracts import UIBundle

EDITABLE = {"decision", "reviewer", "reviewed_at_utc", "comment"}
FIELDS = ["review_id", "event_id", "package_id", "generation_mode", "section", "statement", "tag",
          "claim_ids", "evidence_json", "decision", "reviewer", "reviewed_at_utc", "comment"]


def digest(rows: list[dict]) -> str:
    immutable = [{k: v for k, v in row.items() if k not in EDITABLE} for row in rows]
    return hashlib.sha256(json.dumps(immutable, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def export(bundle_path: Path, output: Path, n: int = 30) -> dict:
    if output.exists() or output.with_suffix(".meta.json").exists():
        raise ValueError("No sobrescribir una revisión humana; usar otra ruta")
    bundle = UIBundle.model_validate_json(bundle_path.read_text(encoding="utf-8"))
    claims = {c.claim_id: c for event in bundle.events for c in event.claims}
    queues = []
    for package in bundle.packages:
        items = [("brief", s) for s in package.brief] + [("script", s) for s in package.script]
        queues.append((package, items))
    rows, seen = [], set()
    while any(items for _, items in queues) and len(rows) < n:
        for package, items in queues:
            if not items or len(rows) >= n:
                continue
            section, sentence = items.pop(0)
            if not sentence.claim_ids or sentence.tag.value not in {"HECHO", "DECLARACION"}:
                continue
            if sentence.text.casefold() in seen:
                continue
            cited = [claims[cid] for cid in sentence.claim_ids if cid in claims]
            if any(ref.field == "descripcion" for claim in cited for ref in claim.evidence):
                raise ValueError("Usar bundle público, sin evidencia de descripciones RSS")
            evidence = [{"claim_id": c.claim_id, "statement": c.statement, "status": c.status.value,
                         "attributed_to": c.attributed_to,
                         "refs": [ref.model_dump(mode="json") for ref in c.evidence]} for c in cited]
            seen.add(sentence.text.casefold())
            rows.append(dict(review_id=f"SR{len(rows)+1:02}", event_id=package.event_id,
                package_id=package.package_id, generation_mode=package.generated_by.mode, section=section,
                statement=sentence.text, tag=sentence.tag.value, claim_ids=json.dumps(sentence.claim_ids),
                evidence_json=json.dumps(evidence, ensure_ascii=False), decision="", reviewer="",
                reviewed_at_utc="", comment=""))
    if len(rows) < n or n < 30:
        raise ValueError("Se requieren al menos 30 afirmaciones distintas; no duplicar para alcanzar n")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    meta = {"created_at": datetime.now(UTC).isoformat(), "snapshot": bundle.snapshot_version,
            "bundle_sha256": hashlib.sha256(bundle_path.read_bytes()).hexdigest(), "rows_sha256": digest(rows),
            "n": len(rows), "generation_modes": sorted({r["generation_mode"] for r in rows}),
            "method": "Primera oración factual por paquete en orden del bundle, rondas brief/script; textos únicos.",
            "scope": "Muestra determinista de paquetes, no aleatoria ni gold humano hasta recibir etiquetas."}
    output.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def measure(path: Path) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    meta = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
    if digest(rows) != meta["rows_sha256"] or len(rows) != meta["n"]:
        raise ValueError("Las afirmaciones/evidencias cambiaron desde la exportación")
    labels, reviewers = [], set()
    for row in rows:
        label = row["decision"].strip().lower().replace("í", "i")
        if label not in {"", "si", "no", "parcial"}:
            raise ValueError(f"Etiqueta inválida en {row['review_id']}")
        if label:
            if not row["reviewer"].strip() or not row["reviewed_at_utc"].strip():
                raise ValueError("Cada etiqueta requiere revisor humano y hora UTC")
            at = datetime.fromisoformat(row["reviewed_at_utc"].replace("Z", "+00:00"))
            if at.utcoffset() is None or at.utcoffset().total_seconds() != 0:
                raise ValueError("La hora de revisión debe estar en UTC")
            labels.append((row["review_id"], label))
            reviewers.add(row["reviewer"].strip())
    complete = len(labels) == len(rows) and len(labels) >= 30
    num = sum(label == "si" for _, label in labels)
    return {"status": "medido" if complete else "no medido", "num": num if complete else None,
            "den": len(labels) if complete else None, "value": num / len(labels) if complete else None,
            "reviewer": sorted(reviewers), "reviewed": len(labels), "required": len(rows),
            "partial": sum(label == "parcial" for _, label in labels),
            "failures": [{"review_id": rid, "decision": label} for rid, label in labels if label != "si"],
            "scope": meta["scope"], "generation_modes": meta["generation_modes"],
            "method": "sí / todas las filas revisadas; parcial no suma al numerador. Requiere toda la muestra (>=30).",
            "evidence": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bundle_sha256": meta["bundle_sha256"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=Path("data/processed/v1/bundle.json"))
    parser.add_argument("--output", type=Path, default=Path("data/labels/support_review.csv"))
    parser.add_argument("--measure", action="store_true")
    args = parser.parse_args()
    print(json.dumps(measure(args.output) if args.measure else export(args.bundle, args.output), ensure_ascii=True))


if __name__ == "__main__":
    main()
