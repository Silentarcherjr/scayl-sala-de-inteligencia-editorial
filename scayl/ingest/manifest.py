"""SHA-256 inventory. A frozen manifest is never silently regenerated."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import yaml

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


def _is_local_only(path: Path) -> bool:
    return (path.parent == Path("responses/gkg") and path.suffix.lower() == ".zip"
            or path == Path("responses/tvn-current/rss.xml"))


def _inventory(directory: Path, *, include_local: bool = False) -> dict:
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Snapshot must not contain symlinks: {path}")
        if not path.is_file() or path == directory / "manifest.json":
            continue
        if not include_local and _is_local_only(path.relative_to(directory)):
            continue
        data = path.read_bytes()
        files[path.relative_to(directory).as_posix()] = {
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "cantidad": _count(path)}
    return files


def _ensure_acquisition_inventory(directory: Path) -> None:
    """Keep local response hashes without requiring those bytes in a clone."""
    target = directory / "acquisition_inventory.json"
    local = {name: meta for name, meta in _inventory(directory, include_local=True).items()
             if _is_local_only(Path(name))}
    if target.exists():
        recorded = json.loads(target.read_text(encoding="utf-8"))["files"]
        # Addenda preserve the original acquisition inventory and raw immutability.
        for addendum in sorted(directory.glob("acquisition_inventory.*.json")):
            for name, entry in json.loads(addendum.read_text(encoding="utf-8"))["files"].items():
                if name in recorded and recorded[name] != entry:
                    raise ValueError(f"Conflicting acquisition inventory entry: {name}")
                recorded[name] = entry
        for name, meta in local.items():
            entry = recorded.get(name, {})
            if (entry.get("sha256") != meta["sha256"] or entry.get("bytes") != meta["bytes"]
                    or entry.get("disponibilidad") != "solo local"):
                raise ValueError(f"Local acquisition inventory mismatch: {name}")
        return
    write_once(target, json_bytes({"status": "acquisition_provenance",
               "created_at": utc_now(), "files": {
                   name: {**meta, "disponibilidad": "solo local"} for name, meta in local.items()}}))


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
    _ensure_acquisition_inventory(directory)
    sources = json.loads((directory / "fuentes.json").read_text(encoding="utf-8"))
    requests = [json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(directory.rglob("*.request.json"))]
    window = yaml.safe_load((Path(__file__).parents[1] / "config" / "data_window.v1.yaml")
                            .read_text(encoding="utf-8"))
    result = {"version": directory.name, "fecha_corte_UTC": window["cutoff_utc"],
              "fecha_congelacion_UTC": utc_now(), "consultas": requests,
              "fuentes": sources, "archivos": _inventory(directory),
              "transformaciones": [
                  "GDELT: URL normalizada y deduplicada; ID SHA-256 de URL; seendate es detección, publicación nula.",
                  "WB: producto de seis países, seis indicadores y 2010–2024; valores ausentes son null explícito.",
                  "USGS: unir páginas; excluir el instante 2025-01-01T00:00:00Z del límite inclusivo de API.",
                  "RSS TVN: pubDate dentro de C-01; detección nula; sin descripciones en el corpus.",
                  "USGS extensión AP-004 separada de los eventos oficiales de 2024.",
                  "Raw 2025 conservado; exclusiones fuera_de_ventana_C-01 en assembly-c01.json."]}
    if (directory / "assembly-c01.json").exists():
        audit = json.loads((directory / "assembly-c01.json").read_text(encoding="utf-8"))
        result["cobertura_efectiva"] = {key: audit[key] for key in
                                      ("window", "news", "tvn", "effective_start", "effective_end",
                                       "target_30_days", "extended_90_days")}
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


def declare_addition(directory: str | Path, *, parent_sha256: str, version: str) -> dict:
    """Explicitly authorized expansion; archive the parent and reject edits to existing raw."""
    directory = Path(directory)
    target = directory / "manifest.json"
    parent_bytes = target.read_bytes()
    if hashlib.sha256(parent_bytes).hexdigest() != parent_sha256:
        raise ValueError("Parent manifest fingerprint does not match")
    parent = json.loads(parent_bytes)
    actual = _inventory(directory)
    for name, meta in parent["archivos"].items():
        if actual.get(name) != meta:
            raise ValueError(f"Existing raw changed: {name}")
    added = sorted(actual.keys() - parent["archivos"].keys())
    if not added:
        raise ValueError("No new files to declare")
    _ensure_acquisition_inventory(directory)
    archive = f"manifest.before-{parent_sha256[:12]}.json"
    write_once(directory / archive, parent_bytes)
    sources_path = directory / "fuentes.recientes.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8")) if sources_path.exists() else []
    result = {**parent, "version": version, "fecha_congelacion_UTC": utc_now(),
              "parent_manifest": {"file": archive, "sha256": parent_sha256},
              "adicion_declarada": added, "archivos": _inventory(directory),
              "fuentes": parent["fuentes"] + sources,
              "consultas": [json.loads(p.read_text(encoding="utf-8"))
                            for p in sorted(directory.rglob("*.request.json"))],
              "transformaciones": parent["transformaciones"] + [
                  ("B-13/B-14: adición autorizada de ACP/INEC; bytes raw anteriores intactos. "
                  "Detalles y ausencias en addition-recent-official.json; fuentes.recientes.json amplía fuentes sin sobrescribir el original.")]}
    target.write_bytes(json_bytes(result))
    return result


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
