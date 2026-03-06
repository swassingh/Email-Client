"""Shared email store for NovaMail POC (HTTP server and Streamlit app)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

# Paths relative to this file: app/store.py -> app/ -> app/data/emails.json
_APP_DIR = Path(__file__).resolve().parent
DATA_DIR = _APP_DIR / "data"
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
    email_type: str  # Valid types: inbox, sent, draft, scheduled, spam, junk, trash
    scheduled_at: str | None = None  # ISO datetime string for when email should be sent


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

    def list(
        self,
        recipient: str | None = None,
        sender: str | None = None,
        email_type: str | None = None,
    ) -> list[dict]:
        rows = self._load()

        # Migrate old emails without type field
        migrated = False
        for row in rows:
            if "email_type" not in row:
                row["email_type"] = self._determine_type(row, recipient, sender)
                migrated = True

        if migrated:
            self._save(rows)

        # Apply filters
        if recipient:
            rows = [r for r in rows if r["recipient"].lower() == recipient.lower()]
        if sender:
            rows = [r for r in rows if r["sender"].lower() == sender.lower()]
        if email_type:
            rows = [
                r
                for r in rows
                if r.get("email_type", "inbox").lower() == email_type.lower()
            ]

        return sorted(rows, key=lambda x: x["id"], reverse=True)

    def _determine_type(
        self,
        email: dict,
        default_recipient: str | None = None,
        default_sender: str | None = None,
    ) -> str:
        if default_sender and email.get("sender", "").lower() == default_sender.lower():
            return "sent"
        if (
            default_recipient
            and email.get("recipient", "").lower() == default_recipient.lower()
        ):
            return "inbox"
        return "inbox"

    def create(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        email_type: str = "inbox",
        scheduled_at: str | None = None,
    ) -> dict:
        rows = self._load()
        next_id = max([r["id"] for r in rows], default=0) + 1
        email = Email(
            id=next_id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            created_at=now_iso(),
            email_type=email_type,
            scheduled_at=scheduled_at,
        )
        rows.append(asdict(email))
        self._save(rows)
        return asdict(email)

    def update_type(self, email_id: int, new_type: str) -> dict | None:
        rows = self._load()
        for row in rows:
            if row["id"] == email_id:
                row["email_type"] = new_type
                self._save(rows)
                return row
        return None

    def get_by_id(self, email_id: int) -> dict | None:
        rows = self._load()
        for row in rows:
            if row["id"] == email_id:
                return row
        return None
