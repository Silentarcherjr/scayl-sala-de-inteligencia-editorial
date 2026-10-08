"""One-command offline demo (H-05 video, rehearsals): no internet, no GPU, no build.

    python scripts/demo_offline.py          # then turn Wi-Fi off and open http://localhost:8501

Uses the reviewed public bundle and LLM cache in deploy/artifacts/v1 (PR #55): 165 events, top 15 with
precomputed qwen3:8b outputs, no RSS descriptions. It copies the bundle to data/processed/v1/ (ignored by
git), forces cache mode and starts Streamlit. Nothing is downloaded and nothing leaves the machine.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "deploy" / "artifacts" / "v1"


def prepare() -> dict[str, str]:
    bundle = ARTIFACTS / "bundle.public.json"
    if not bundle.exists():
        sys.exit(f"Falta {bundle}. Ejecuta `git pull` en main.")
    target = ROOT / "data" / "processed" / "v1" / "bundle.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bundle, target)
    env = dict(os.environ, SCAYL_LLM_MODE="cache", SCAYL_LLM_CACHE=str(ARTIFACTS / "llm"),
               SCAYL_SNAPSHOT_DIR="data/raw/v1", PYTHONPATH=str(ROOT))
    print(f"Bundle de demo listo: {target}")
    return env


def main() -> None:
    env = prepare()
    print("Abre http://localhost:8501 · ya puedes apagar el wifi · Ctrl+C para salir")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(ROOT / "app" / "Home.py"),
                    "--server.headless", "true", "--server.address", "localhost", "--browser.gatherUsageStats", "false"], env=env, check=False)


if __name__ == "__main__":
    main()
