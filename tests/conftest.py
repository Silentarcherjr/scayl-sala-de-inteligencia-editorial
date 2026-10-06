import json
from pathlib import Path

import pytest

from scayl.contracts import UIBundle

FIXTURE = Path(__file__).parent / "fixtures" / "ui_bundle.example.json"


@pytest.fixture
def bundle() -> UIBundle:
    return UIBundle.model_validate(json.loads(FIXTURE.read_text(encoding="utf-8")))


@pytest.fixture
def events(bundle):
    return {e.event_id: e for e in bundle.events}
