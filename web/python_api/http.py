"""Bounded JSON transport for Vercel's BaseHTTPRequestHandler."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from pydantic import ValidationError

from python_api.actions import ask, check, review

ACTIONS = {"ask": ask, "check": check, "review": review}

MAX_BODY = 8192


def dispatch(action: str, payload: object) -> tuple[int, dict]:
    if not isinstance(payload, dict):
        return 400, {"error": "Se requiere un objeto JSON."}
    try:
        return 200, ACTIONS[action](payload)
    except ValidationError as exc:
        fields = sorted({str(error["loc"][0]) for error in exc.errors() if error["loc"]})
        return 422, {"error": "Entrada inválida. Revisa los campos y sus límites.", "fields": fields}
    except KeyError:
        return 404, {"error": "El caso no existe en el snapshot público."}
    except ValueError as exc:
        return 422, {"error": str(exc)}


class JSONHandler(BaseHTTPRequestHandler):
    action: str

    def do_POST(self):
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            self.send_json(415, {"error": "Usa Content-Type: application/json."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Content-Length inválido."})
            return
        if size <= 0 or size > MAX_BODY:
            self.send_json(413, {"error": "Cuerpo vacío o superior a 8192 bytes."})
            return
        try:
            payload = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeError):
            self.send_json(400, {"error": "JSON inválido."})
            return
        try:
            status, body = dispatch(self.action, payload)
        except Exception:  # noqa: BLE001 - HTTP boundary must return a sanitized 503
            # Do not leak paths, source text, request content or internal exceptions.
            status, body = 503, {"error": "Servicio no disponible. Usa las respuestas guardadas y vuelve a intentarlo."}
        self.send_json(status, body)

    def do_GET(self):
        self.send_json(405, {"error": "Usa POST con un objeto JSON."})

    do_PUT = do_GET
    do_DELETE = do_GET
    do_PATCH = do_GET

    def send_json(self, status: int, body: dict):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(data)))
        if status == 405:
            self.send_header("Allow", "POST")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        # No question, reviewer name or justification in application logs.
        pass
