#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import smtplib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
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
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, rows: list[dict]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(rows, file, indent=2)

    def list(self, recipient: str | None = None) -> list[dict]:
        rows = self._load()
        if recipient:
            rows = [row for row in rows if row["recipient"].lower() == recipient.lower()]
        return sorted(rows, key=lambda row: row["id"], reverse=True)

    def create(self, sender: str, recipient: str, subject: str, body: str) -> dict:
        rows = self._load()
        next_id = max([row["id"] for row in rows], default=0) + 1
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


class SMTPConfigError(RuntimeError):
    pass


class EmailDelivery:
    @staticmethod
    def _read_config() -> dict:
        cfg = {
            "host": os.environ.get("SMTP_HOST", "").strip(),
            "port": int(os.environ.get("SMTP_PORT", "587")),
            "user": os.environ.get("SMTP_USER", "").strip(),
            "password": os.environ.get("SMTP_PASS", "").strip(),
            "from_addr": os.environ.get("SMTP_FROM", os.environ.get("SMTP_USER", "")).strip(),
            "use_tls": os.environ.get("SMTP_USE_TLS", "true").lower() == "true",
            "use_ssl": os.environ.get("SMTP_USE_SSL", "false").lower() == "true",
        }
        required = ["host", "port", "user", "password", "from_addr"]
        missing = [key for key in required if not cfg.get(key)]
        if missing:
            raise SMTPConfigError(
                "SMTP is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM."
            )
        return cfg

    @staticmethod
    def send_email(recipient: str, subject: str, body: str) -> None:
        cfg = EmailDelivery._read_config()

        message = EmailMessage()
        message["From"] = cfg["from_addr"]
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        if cfg["use_ssl"]:
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=15) as server:
                server.login(cfg["user"], cfg["password"])
                server.send_message(message)
            return

        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as server:
            server.ehlo()
            if cfg["use_tls"]:
                server.starttls()
                server.ehlo()
            server.login(cfg["user"], cfg["password"])
            server.send_message(message)


class Handler(BaseHTTPRequestHandler):
    server_version = "POCEmailServer/1.0"

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
            missing = [key for key in required if not payload.get(key)]
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
            subject = "NovaMail POC Vision + Architecture for Manager Review"
            email_body = (
                "Hi Swastik,\n\n"
                "Sharing the latest NovaMail POC package.\n"
                "- PM vision emphasizes AI-first triage and speed\n"
                "- Team lead architecture introduces SMTP delivery + intelligent inbox lanes\n"
                "- UX redesign introduces Focus Now / Quick Wins / FYI streams\n"
                "- Backend now supports real SMTP delivery when configured\n\n"
                "Regards,\nPM — NovaMail"
            )

            try:
                EmailDelivery.send_email(recipient=recipient, subject=subject, body=email_body)
            except SMTPConfigError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            except Exception as exc:  # smtp/network runtime failures
                self._send_json({"error": f"SMTP delivery failed: {exc}"}, HTTPStatus.BAD_GATEWAY)
                return

            email = STORE.create(
                sender=os.environ.get("SMTP_FROM", "pm@novamail.dev"),
                recipient=recipient,
                subject=subject,
                body=email_body,
            )
            self._send_json(
                {
                    "status": "sent",
                    "message": f"Architecture email sent to {recipient}.",
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
