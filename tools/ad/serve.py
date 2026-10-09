"""Local mirror of the Vercel deployment: static web/out + the same Python API handlers (port 3000).

    python tools/ad/serve.py web      # after: cd web && npm ci && node scripts/prepare-python.mjs && npm run build
"""
import http.server
import sys
from pathlib import Path

WEB = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(WEB))
from python_api.http import JSONHandler


class Handler(http.server.SimpleHTTPRequestHandler):
    send_json = JSONHandler.send_json
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(WEB / "out"), **k)
    def do_POST(self):
        if self.path.split("?")[0] in ("/api/ask", "/api/review", "/api/check"):
            self.action = self.path.split("?")[0].rsplit("/", 1)[1]
            return JSONHandler.do_POST(self)
        self.send_error(404)
    def log_message(self, *a): pass

http.server.ThreadingHTTPServer(("127.0.0.1", 3000), Handler).serve_forever()
