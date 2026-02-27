#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
DATA_DIR = ROOT / "app" / "data"
DATA_FILE = DATA_DIR / "emails.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Email:
    id: int
    sender: str
    recipient: str
    subject: str
    body: str
    created_at: str


class EmailStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save([])

    def _load(self) -> list[dict]:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, rows: list[dict]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)

    def list(self, recipient: str | None = None) -> list[dict]:
        rows = self._load()
        if recipient:
            rows = [r for r in rows if r["recipient"].lower() == recipient.lower()]
        return sorted(rows, key=lambda x: x["id"], reverse=True)

    def create(self, sender: str, recipient: str, subject: str, body: str) -> dict:
        rows = self._load()
        next_id = max([r["id"] for r in rows], default=0) + 1
        email = Email(
            id=next_id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            created_at=now_iso(),
        )
        rows.append(asdict(email))
        self._save(rows)
        return asdict(email)


STORE = EmailStore(DATA_FILE)


class Handler(BaseHTTPRequestHandler):
    server_version = "POCEmailServer/0.2"

    def _send_json(self, payload: dict | list, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _mime_for_path(self, path: Path) -> str:
        return {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
        }.get(path.suffix.lower(), "text/plain; charset=utf-8")

    def _safe_web_path(self, rel: str) -> Path | None:
        target = (WEB_DIR / rel).resolve()
        try:
            target.relative_to(WEB_DIR.resolve())
        except ValueError:
            return None
        return target

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", self._mime_for_path(path))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            self._send_json({"status": "ok", "time": now_iso()})
            return

        if parsed.path == "/api/emails":
            params = parse_qs(parsed.query)
            recipient = params.get("recipient", [None])[0]
            self._send_json(STORE.list(recipient=recipient))
            return

        if parsed.path in {"/", "/index.html", "/web/index.html"}:
            self._send_file(WEB_DIR / "index.html")
            return

        if parsed.path.startswith("/static/"):
            rel = parsed.path.replace("/static/", "", 1)
            safe = self._safe_web_path(rel)
            if safe is None:
                self.send_error(HTTPStatus.BAD_REQUEST)
                return
            self._send_file(safe)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            self._send_json({"error": "Invalid JSON payload."}, HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == "/api/emails":
            required = ["sender", "recipient", "subject", "body"]
            missing = [k for k in required if not payload.get(k)]
            if missing:
                self._send_json(
                    {"error": f"Missing required fields: {', '.join(missing)}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            email = STORE.create(
                sender=str(payload["sender"]).strip(),
                recipient=str(payload["recipient"]).strip(),
                subject=str(payload["subject"]).strip(),
                body=str(payload["body"]).strip(),
            )
            self._send_json(email, HTTPStatus.CREATED)
            return

        if parsed.path == "/api/send-architecture-email":
            recipient = str(payload.get("recipient", "")).strip() or "Swastik.Singh@gmail.com"
            email = STORE.create(
                sender="pm@novamail.dev",
                recipient=recipient,
                subject="NovaMail POC Vision + Architecture for Manager Review",
                body=(
                    "Hi Swastik, sharing the NovaMail POC architecture: frontend static UI, "
                    "Python API service, JSON persistence, with a scale plan to PostgreSQL + auth + AI jobs."
                ),
            )
            self._send_json(
                {
                    "status": "sent-simulated",
                    "message": "Architecture email recorded in outbox/inbox for demo purposes.",
                    "email": email,
                },
                HTTPStatus.CREATED,
            )
            return

        self.send_error(HTTPStatus.NOT_FOUND)


def run() -> None:
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"POC Email Client server listening on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
