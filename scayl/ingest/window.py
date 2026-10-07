"""Read the Lead-owned data window without duplicating dates in fetchers."""
from datetime import datetime, timedelta
from pathlib import Path

import yaml


def data_window() -> dict:
    return yaml.safe_load((Path(__file__).parents[1] / "config/data_window.v1.yaml")
                          .read_text(encoding="utf-8"))


def news_window(*, target: bool = False, extended: bool = False) -> tuple[datetime, datetime]:
    cfg = data_window()["news"]
    end = datetime.fromisoformat(cfg["end_exclusive"])
    start = datetime.fromisoformat(cfg["start_inclusive"])
    if target or extended:
        days = cfg["max_days_before_cutoff" if extended else "target_days_before_cutoff"]
        start = max(start, end - timedelta(days=days))
    return start, end
