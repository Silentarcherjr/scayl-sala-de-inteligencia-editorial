"""Blind editor handoff: no priority, model labels, or source ordering."""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

from .common import write_csv


def export(snapshot: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError("Keep the original blind handoff; do not reshuffle it")
    with (snapshot / "noticias.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates = [{"id_noticia": row["id_noticia"], "titulo": row["titulo"], "medio": row["medio"],
                   "fecha_publicacion": row["fecha_publicacion"],
                   "fecha_deteccion": row["fecha_deteccion"]} for row in rows]
    random.SystemRandom().shuffle(candidates)
    write_csv(output, candidates, ["id_noticia", "titulo", "medio", "fecha_publicacion", "fecha_deteccion"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=Path("data/raw/v1"))
    parser.add_argument("--output", type=Path, default=Path("data/labels/editor_candidates.csv"))
    args = parser.parse_args()
    export(args.snapshot, args.output)
