"""All M>=3 events in the official 2024 bounding box, with pagination."""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from .common import download, json_bytes, write_once
from .window import news_window

PARAMS = {"format": "geojson", "starttime": "2024-01-01T00:00:00",
          "endtime": "2025-01-01T00:00:00", "minlatitude": 5, "maxlatitude": 12,
          "minlongitude": -86, "maxlongitude": -76, "minmagnitude": 3,
          "orderby": "time-asc", "limit": 20000}


def fetch(directory: Path, *, extension: bool = False) -> dict:
    params = dict(PARAMS)
    if extension:
        start, end = news_window()
        params.update(starttime=start.isoformat(), endtime=end.isoformat())
    else:
        start = datetime.fromisoformat(params["starttime"]).replace(tzinfo=UTC)
        end = datetime.fromisoformat(params["endtime"]).replace(tzinfo=UTC)
    features = []
    offset = 1
    while True:
        content, _ = download(directory / ("responses/usgs-ext" if extension else "responses/usgs"),
                              f"events.{offset}.json", "https://earthquake.usgs.gov/fdsnws/event/1/query",
                              {**params, "offset": offset})
        payload = json.loads(content)
        if payload.get("type") != "FeatureCollection":
            raise ValueError("USGS did not return a FeatureCollection")
        features.extend(payload["features"])
        if len(payload["features"]) < params["limit"]:
            break
        offset += params["limit"]
    # The service endtime is inclusive; the official interval is half-open.
    start_ms, end_ms = int(start.timestamp() * 1000), int(end.timestamp() * 1000)
    features = [feature for feature in features if start_ms <= feature["properties"]["time"] < end_ms]
    if len({feature["id"] for feature in features}) != len(features):
        raise ValueError("USGS pagination contains duplicate event IDs")
    result = {"type": "FeatureCollection", "features": features}
    write_once(directory / ("eventos_ext.geojson" if extension else "eventos.geojson"), json_bytes(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/v1"))
    parser.add_argument("--extension", action="store_true")
    args = parser.parse_args()
    fetch(args.output, extension=args.extension)
