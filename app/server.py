#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from app.store import DATA_FILE, EmailStore, now_iso

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
ARCHITECTURE_DOC = ROOT / "docs" / "team" / "Team_Architecture.md"

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
            sender = params.get("sender", [None])[0]
            email_type = params.get("type", [None])[0]
            self._send_json(STORE.list(recipient=recipient, sender=sender, email_type=email_type))
            return

        if parsed.path in {"/", "/index.html", "/web/index.html"}:
            self._send_file(WEB_DIR / "index.html")
            return

        if parsed.path.startswith("/api/emails/") and parsed.path.count("/") == 3:
            # GET /api/emails/{id}
            try:
                email_id = int(parsed.path.split("/")[-1])
                email = STORE.get_by_id(email_id)
                if email:
                    self._send_json(email)
                else:
                    self.send_error(HTTPStatus.NOT_FOUND)
                return
            except ValueError:
                self.send_error(HTTPStatus.BAD_REQUEST)
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

            # Determine email type based on logic:
            # - If explicitly provided, use it
            # - If sender is default sender (pm@novamail.dev), default to "sent"
            # - Otherwise, default to "inbox"
            # Valid types: inbox, sent, draft, scheduled, spam, junk, trash
            explicit_type = payload.get("email_type", "").strip().lower()
            valid_types = ["inbox", "sent", "draft", "scheduled", "spam", "junk", "trash"]
            
            if explicit_type in valid_types:
                email_type = explicit_type
            else:
                # Auto-determine based on sender
                default_sender = "pm@novamail.dev"
                if str(payload["sender"]).strip().lower() == default_sender.lower():
                    email_type = "sent"
                else:
                    email_type = "inbox"
            
            # Get scheduled_at if provided (for scheduled emails)
            scheduled_at = payload.get("scheduled_at", "").strip() or None
            
            email = STORE.create(
                sender=str(payload["sender"]).strip(),
                recipient=str(payload["recipient"]).strip(),
                subject=str(payload["subject"]).strip(),
                body=str(payload["body"]).strip(),
                email_type=str(email_type).strip(),
                scheduled_at=scheduled_at,
            )
            self._send_json(email, HTTPStatus.CREATED)
            return

        if parsed.path == "/api/send-architecture-email":
            recipient = str(payload.get("recipient", "")).strip() or "Swastik.Singh@gmail.com"
            
            # Read the full architecture document
            architecture_body = ""
            if ARCHITECTURE_DOC.exists():
                try:
                    architecture_body = ARCHITECTURE_DOC.read_text(encoding="utf-8")
                except Exception as e:
                    architecture_body = f"Error reading architecture document: {e}"
            else:
                architecture_body = "Architecture document not found."
            
            email = STORE.create(
                sender="pm@novamail.dev",
                recipient=recipient,
                subject="NovaMail POC Architecture Document — Complete",
                body=architecture_body,
                email_type="sent",
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
    
    def do_PATCH(self) -> None:
        """Handle PATCH requests for updating email types."""
        parsed = urlparse(self.path)
        
        if parsed.path.startswith("/api/emails/") and parsed.path.count("/") == 3:
            try:
                email_id = int(parsed.path.split("/")[-1])
            except ValueError:
                self._send_json({"error": "Invalid email ID."}, HTTPStatus.BAD_REQUEST)
                return
            
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                payload = json.loads(body.decode("utf-8")) if body else {}
            except Exception:
                self._send_json({"error": "Invalid JSON payload."}, HTTPStatus.BAD_REQUEST)
                return
            
            # Get the current email to check its type
            current_email = STORE.get_by_id(email_id)
            if not current_email:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            
            # Validate email_type
            new_type = payload.get("email_type", "").strip().lower()
            valid_types = ["inbox", "sent", "draft", "scheduled", "spam", "junk", "trash"]
            
            if new_type not in valid_types:
                self._send_json(
                    {"error": f"Invalid email_type. Must be one of: {', '.join(valid_types)}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            
            # Prevent moving sent emails to anything except trash
            current_type = current_email.get("email_type", "").lower()
            if current_type == "sent" and new_type != "trash":
                self._send_json(
                    {"error": "Cannot move sent emails. Sent emails can only be moved to trash."},
                    HTTPStatus.FORBIDDEN,
                )
                return
            
            updated = STORE.update_type(email_id, new_type)
            if updated:
                self._send_json(updated)
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
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
