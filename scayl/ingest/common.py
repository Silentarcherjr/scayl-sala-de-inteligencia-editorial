"""Immutable public-source downloads and explicit CSV null representation."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

NULL = "null"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_once(path: Path, content: bytes) -> None:
    """Identical reruns are harmless; changed bytes require a new snapshot."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise FileExistsError(f"Immutable file differs: {path}")
        return
    with path.open("xb") as handle:
        handle.write(content)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: NULL if row.get(field) is None else row[field] for field in fields})
    write_once(path, stream.getvalue().encode("utf-8"))


def download(directory: Path, name: str, url: str, params: dict | None = None) -> tuple[bytes, dict]:
    """Cache response bytes and request provenance; never use account credentials."""
    full_url = url + ("?" + urlencode(params) if params else "")
    target = directory / name
    receipt = directory / (name + ".request.json")
    if target.exists() and receipt.exists():
        meta = json.loads(receipt.read_text(encoding="utf-8"))
        content = target.read_bytes()
        if meta["url"] != full_url or hashlib.sha256(content).hexdigest() != meta["sha256"]:
            raise ValueError(f"Cached request mismatch: {target}")
        return content, meta
    request = Request(full_url, headers={"User-Agent": "SCAYL-snapshot/1.0 (public metadata research)"})
    attempts = []
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as response:
                content = response.read()
                meta = {"url": full_url, "fecha_extraccion": utc_now(), "status": response.status,
                        "content_type": response.headers.get("Content-Type"),
                        "sha256": hashlib.sha256(content).hexdigest(), "previous_failures": attempts}
            break
        except (HTTPError, URLError, TimeoutError) as error:
            attempts.append({"at": utc_now(), "error": str(error)})
            if attempt == 2 or isinstance(error, HTTPError) and error.code not in (429, 500, 502, 503, 504):
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                write_once(directory / "failures" / f"{name}.{stamp}.json",
                           json_bytes({"url": full_url, "attempts": attempts, "success": False}))
                raise
            retry_after = error.headers.get("Retry-After") if isinstance(error, HTTPError) else None
            pause = float(retry_after) if retry_after and retry_after.isdigit() else 15 * (attempt + 1)
            time.sleep(pause)
    write_once(target, content)
    write_once(receipt, json_bytes(meta))
    return content, meta
