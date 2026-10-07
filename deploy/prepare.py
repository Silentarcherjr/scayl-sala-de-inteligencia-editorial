"""Prepare an allowlisted HF Docker Space folder locally. Never upload or read credentials."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from scayl.contracts import UIBundle

ROOT = Path(__file__).resolve().parents[1]


def check_public(value) -> None:
    if isinstance(value, dict):
        if value.get("descripcion") not in (None, "") or value.get("field") == "descripcion":
            raise ValueError("El artefacto contiene una descripción RSS o una cita a ella")
        for item in value.values():
            check_public(item)
    elif isinstance(value, list):
        for item in value:
            check_public(item)


def prepare(bundle_path: Path, cache: Path, destination: Path) -> dict:
    if destination.exists():
        raise ValueError("El destino ya existe; usar una carpeta nueva para no sobrescribir trabajo")
    raw = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle = UIBundle.model_validate(raw)
    check_public(raw)
    if bundle.snapshot_version != "v1" or bundle.reviews:
        raise ValueError("Se requiere snapshot v1 público, sin decisiones humanas")
    if any(p.generated_by.mode == "live" for p in bundle.packages):
        raise ValueError("Regenerar con make public-bundle: hay paquetes marcados live")
    # Only include explicitly inspected cache JSON, never state/raw/labels/env/model weights.
    cache_entries = []
    for path in sorted(cache.glob("*.json")):
        entry = json.loads(path.read_text(encoding="utf-8"))
        check_public(entry)
        if set(entry) != {"data", "meta"}:
            raise ValueError(f"Formato de caché inesperado: {path.name}")
        cache_entries.append(path)
    destination.mkdir(parents=True)
    def copy(source: Path, relative: str) -> None:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    for folder in ("app", "scayl"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and path.suffix in {".py", ".yaml", ".txt", ".md"} and "__pycache__" not in path.parts:
                copy(path, path.relative_to(ROOT).as_posix())
    for source, target in [("requirements.txt", "requirements.txt"),
                           (".streamlit/config.toml", ".streamlit/config.toml"),
                           ("deploy/Dockerfile", "Dockerfile"), ("deploy/SPACE_README.md", "README.md"),
                           ("deploy/space.py", "app/space.py"), ("deploy/space.py", "deploy/space.py"),
                           ("deploy/runtime.py", "deploy/runtime.py")]:
        copy(ROOT / source, target)
    # Gate the staged page files too: direct file-based navigation must never bypass the entrypoint.
    # Keep original modules intact in views, including any future imports/docstrings.
    pages = [destination / "app/Home.py", *sorted((destination / "app/pages").glob("*.py"))]
    for page in pages:
        relative = page.relative_to(destination / "app")
        original = destination / "app/_protected" / relative
        original.parent.mkdir(parents=True, exist_ok=True)
        page.replace(original)
        page.write_text("from deploy.space import hosted_frame\nhosted_frame()\n"
                        "import runpy\nfrom pathlib import Path\n"
                        f"runpy.run_path(str(Path(__file__).resolve().parents[{len(relative.parts) - 1}] / "
                        f"'_protected/{relative.as_posix()}'), run_name='__main__')\n", encoding="utf-8")
    copy(bundle_path, "data/processed/v1/bundle.json")
    (destination / "data/cache/llm").mkdir(parents=True)
    (destination / "data/cache/llm/.gitkeep").touch()
    for path in cache_entries:
        copy(path, f"data/cache/llm/{path.name}")
    report = ROOT / "eval/results/latest.json"
    if report.exists():
        copy(report, "eval/results/latest.json")
    (destination / ".dockerignore").write_text(".git\n.env\n**/__pycache__\ndata/state\n", encoding="utf-8")
    manifest = {"prepared_at": datetime.now(UTC).isoformat(), "published": False,
        "snapshot": bundle.snapshot_version, "signals": len(bundle.news), "events": len(bundle.events),
        "cache_entries": len(cache_entries), "package_modes": dict(Counter(p.generated_by.mode for p in bundle.packages)),
        "limitations": ["Sin cache disponible, las respuestas caen a template; no son salidas de un LLM.",
                        "Revisar procedencia de la caché: --public elimina descripciones de news, no reconstruye entradas antiguas."],
        "files": {p.relative_to(destination).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(destination.rglob("*")) if p.is_file()}}
    (destination / "PREPARATION.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=ROOT / "data/processed/v1/bundle.json")
    parser.add_argument("--cache", type=Path, default=ROOT / "data/cache/llm")
    parser.add_argument("--out", type=Path, default=ROOT / "deploy/stage")
    args = parser.parse_args()
    result = prepare(args.bundle, args.cache, args.out)
    print(json.dumps({key: val for key, val in result.items() if key != "files"}, ensure_ascii=True))


if __name__ == "__main__":
    main()
