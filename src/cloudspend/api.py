"""Small deterministic HTTP API suitable for an authenticated Cloud Run service."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .detector import connect, detect, load_records

MAX_BODY_BYTES = 1_000_000


def analyze_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise ValueError("request body must contain a records array")
    records = payload["records"]
    db = connect()
    try:
        load_records(db, records)
        anomalies = detect(db)
    finally:
        db.close()
    return {
        "synthetic_demo": True,
        "anomaly_count": len(anomalies),
        "anomalies": [item.to_dict() for item in anomalies],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "CloudSpend/1"

    def _json(self, status: int, body: dict[str, Any]) -> None:
        encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path == "/healthz":
            self._json(200, {"status": "ok"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/v1/anomalies":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                raise ValueError("request body size is invalid")
            payload = json.loads(self.rfile.read(length))
            self._json(200, analyze_payload(payload))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})

    def log_message(self, format: str, *args: object) -> None:
        print(json.dumps({"remote": self.address_string(), "message": format % args}))


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
