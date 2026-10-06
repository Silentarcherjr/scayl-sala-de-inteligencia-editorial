"""All M>=3 events in the official 2024 bounding box, with pagination."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .common import download, json_bytes, write_once

PARAMS = {"format": "geojson", "starttime": "2024-01-01T00:00:00",
          "endtime": "2025-01-01T00:00:00", "minlatitude": 5, "maxlatitude": 12,
          "minlongitude": -86, "maxlongitude": -76, "minmagnitude": 3,
          "orderby": "time-asc", "limit": 20000}


def fetch(directory: Path) -> dict:
    features = []
    offset = 1
    while True:
        content, _ = download(directory / "responses/usgs", f"events.{offset}.json",
                              "https://earthquake.usgs.gov/fdsnws/event/1/query", {**PARAMS, "offset": offset})
        payload = json.loads(content)
        if payload.get("type") != "FeatureCollection":
            raise ValueError("USGS did not return a FeatureCollection")
        features.extend(payload["features"])
        if len(payload["features"]) < PARAMS["limit"]:
            break
        offset += PARAMS["limit"]
    # The service endtime is inclusive; the official interval is half-open.
    end_ms = int(datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    features = [feature for feature in features if feature["properties"]["time"] < end_ms]
    if len({feature["id"] for feature in features}) != len(features):
        raise ValueError("USGS pagination contains duplicate event IDs")
    result = {"type": "FeatureCollection", "features": features}
    write_once(directory / "eventos.geojson", json_bytes(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/v1"))
    fetch(parser.parse_args().output)
