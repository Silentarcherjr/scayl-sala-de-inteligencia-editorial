"""Human review: append-only SQLite log + Notion outbox + traceability receipt (L-12, L-16).

The five official states. "aprobado_como_borrador" is NOT publication; there is no publish action.
Works fully offline: Notion sync is only queued (data/state/notion_outbox.jsonl).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from scayl.contracts import Event, ReviewRecord, ReviewState, StoryPackage, can_transition

DEFAULT_STATE_DIR = Path("data/state")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    package_id TEXT,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    justification TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    evidence_snapshot_sha256 TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reviews_event ON reviews(event_id, decided_at);
"""


class ReviewError(ValueError):
    pass


def canonical_sha256(obj) -> str:
    data = obj.model_dump(mode="json") if hasattr(obj, "model_dump") else obj
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ReviewStore:
    def __init__(self, state_dir: Path = DEFAULT_STATE_DIR, snapshot_sha256: str | None = None):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        (self.state_dir / "receipts").mkdir(exist_ok=True)
        self.snapshot_sha256 = snapshot_sha256
        self.db_path = self.state_dir / "reviews.sqlite"
        with self._conn() as conn:
            conn.executescript(_SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def history(self, event_id: str) -> list[ReviewRecord]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT review_id, event_id, package_id, from_state, to_state, reviewer, justification, "
                "decided_at, evidence_snapshot_sha256 FROM reviews WHERE event_id = ? ORDER BY decided_at, rowid",
                (event_id,),
            ).fetchall()
        keys = ("review_id", "event_id", "package_id", "from_state", "to_state", "reviewer", "justification",
                "decided_at", "evidence_snapshot_sha256")
        return [ReviewRecord.model_validate(dict(zip(keys, r))) for r in rows]

    def current_state(self, event_id: str) -> ReviewState:
        hist = self.history(event_id)
        return hist[-1].to_state if hist else ReviewState.NUEVO

    def record(
        self,
        event: Event,
        to_state: ReviewState,
        reviewer: str,
        justification: str,
        package: StoryPackage | None = None,
        now: datetime | None = None,
    ) -> ReviewRecord:
        reviewer, justification = reviewer.strip(), justification.strip()
        if not reviewer:
            raise ReviewError("El revisor es obligatorio.")
        if not justification:
            raise ReviewError("La justificación es obligatoria.")
        src = self.current_state(event.event_id)
        if not can_transition(src, to_state):
            raise ReviewError(f"Transición no permitida: {src.value} → {to_state.value}")

        rec = ReviewRecord(
            review_id=f"REV-{uuid.uuid4().hex[:12]}",
            event_id=event.event_id,
            package_id=package.package_id if package else None,
            from_state=src,
            to_state=to_state,
            reviewer=reviewer,
            justification=justification,
            decided_at=now or datetime.now(UTC),
            evidence_snapshot_sha256=canonical_sha256(event),
        )
        with self._conn() as conn:
            d = rec.model_dump(mode="json")
            conn.execute(
                "INSERT INTO reviews VALUES (:review_id, :event_id, :package_id, :from_state, :to_state, "
                ":reviewer, :justification, :decided_at, :evidence_snapshot_sha256)",
                d,
            )
        self._write_receipt(rec, event, package)
        self._enqueue_notion(rec)
        return rec

    def _write_receipt(self, rec: ReviewRecord, event: Event, package: StoryPackage | None) -> Path:
        body = {
            "review": rec.model_dump(mode="json"),
            "snapshot_sha256": self.snapshot_sha256,
            "evidence_snapshot_sha256": rec.evidence_snapshot_sha256,
            "claims": [c.model_dump(mode="json") for c in event.claims],
            "package_id": package.package_id if package else None,
            "package_sha256": canonical_sha256(package) if package else None,
            "generated_by": package.generated_by.model_dump(mode="json") if package else None,
            "note": "Aprobado como borrador NO significa publicado.",
        }
        receipt = {**body, "receipt_sha256": canonical_sha256(body)}
        path = self.state_dir / "receipts" / f"{rec.review_id}.json"
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def receipt(self, review_id: str) -> dict:
        return json.loads((self.state_dir / "receipts" / f"{review_id}.json").read_text(encoding="utf-8"))

    def _enqueue_notion(self, rec: ReviewRecord) -> None:
        item = {
            "op": "upsert_review",
            "page": "05_CASES_AND_EVIDENCE",
            "payload": rec.model_dump(mode="json"),
            "created_at": datetime.now(UTC).isoformat(),
            "synced_at": None,
        }
        with (self.state_dir / "notion_outbox.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def pending_notion(self) -> list[dict]:
        path = self.state_dir / "notion_outbox.jsonl"
        if not path.exists():
            return []
        return [i for i in map(json.loads, path.read_text(encoding="utf-8").splitlines()) if not i["synced_at"]]
