"""POST /api/check: editorial claim checker (Vercel native Python handler)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from python_api.http import JSONHandler


class handler(JSONHandler):
    action = "check"
