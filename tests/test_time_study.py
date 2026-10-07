import csv
from pathlib import Path

import pytest

from scayl.eval.time_study import summarize


def test_empty_study_does_not_claim_saved_time():
    result = summarize(Path("data/labels/time_study.csv"))
    assert result["status"] == "no medido" and result["n"] == 0
    assert result["relative_difference"]["num"] is None


def test_real_pairs_can_show_slowdown_and_missing_pair_stays_unmeasured(tmp_path):
    path = tmp_path / "study.csv"
    with Path("data/labels/time_study.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        row.update(participant="Humano sintético de prueba", manual_seconds="10", assisted_seconds="20",
                   completed_at_utc="2026-10-07T18:00:00Z", manual_output="A", assisted_output="B")
    def save():
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    save()
    result = summarize(path)
    assert result["n"] == 3 and result["difference_seconds"] == -30
    assert result["relative_difference"]["num"] == -30 and result["relative_difference"]["den"] == 30
    rows[0]["assisted_seconds"] = ""
    save()
    assert summarize(path)["status"] == "no medido"
    rows[0]["assisted_seconds"] = "nan"
    save()
    with pytest.raises(ValueError, match="finitas"):
        summarize(path)
