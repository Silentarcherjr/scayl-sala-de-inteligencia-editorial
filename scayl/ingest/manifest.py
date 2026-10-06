"""SHA-256 inventory. A frozen manifest is never silently regenerated."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from .common import json_bytes, utc_now, write_once


def _count(path: Path) -> int | None:
    if path.suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return sum(1 for _ in csv.DictReader(handle))
    if path.suffix in (".json", ".geojson"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError):
            return None
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            for key in ("features", "articles", "items"):
                if isinstance(value.get(key), list):
                    return len(value[key])
    return None


def _inventory(directory: Path) -> dict:
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Snapshot must not contain symlinks: {path}")
        if not path.is_file() or path == directory / "manifest.json":
            continue
        data = path.read_bytes()
        files[path.relative_to(directory).as_posix()] = {
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "cantidad": _count(path)}
    return files


def build_manifest(directory: str | Path) -> dict:
    directory = Path(directory)
    if (directory / "manifest.json").exists():
        differences = verify_manifest(directory)
        if differences:
            raise ValueError(f"Frozen snapshot changed: {differences}")
        return json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    required = ("noticias.csv", "indicadores.csv", "eventos.geojson", "fuentes.json")
    missing = [name for name in required if not (directory / name).is_file()]
    if missing:
        raise ValueError(f"Incomplete snapshot: {missing}")
    sources = json.loads((directory / "fuentes.json").read_text(encoding="utf-8"))
    requests = [json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(directory.rglob("*.request.json"))]
    result = {"version": directory.name, "fecha_corte_UTC": "2025-10-01T00:00:00Z",
              "fecha_congelacion_UTC": utc_now(), "consultas": requests,
              "fuentes": sources, "archivos": _inventory(directory),
              "transformaciones": [
                  "GDELT: URL normalizada y deduplicada; ID SHA-256 de URL; seendate es detección, publicación nula.",
                  "WB: producto de seis países, seis indicadores y 2010–2024; valores ausentes son null explícito.",
                  "USGS: unir páginas; excluir el instante 2025-01-01T00:00:00Z del límite inclusivo de API.",
                  "RSS TVN actual separado del corpus histórico; solo metadatos."]}
    write_once(directory / "manifest.json", json_bytes(result))
    return result


def verify_manifest(directory: str | Path) -> list[str]:
    directory = Path(directory)
    try:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        expected = manifest["archivos"]
        if not isinstance(expected, dict):
            return ["manifest.json: invalid archivos"]
    except (OSError, ValueError, KeyError):
        return ["manifest.json: missing or invalid"]
    actual = _inventory(directory)
    differences = []
    for name in sorted(expected.keys() | actual.keys()):
        if name not in expected:
            differences.append(f"unexpected:{name}")
        elif name not in actual:
            differences.append(f"missing:{name}")
        elif expected[name] != actual[name]:
            differences.append(f"changed:{name}")
    return differences


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        diffs = verify_manifest(args.directory)
        print(json.dumps(diffs))
        raise SystemExit(bool(diffs))
    build_manifest(args.directory)
