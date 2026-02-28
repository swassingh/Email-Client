#!/usr/bin/env python3
"""
Standalone script to send the architecture document via email.
This script can be run independently to send the architecture plans.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Get the project root (parent of scripts directory)
ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_DOC = ROOT / "docs" / "team" / "Team_Architecture.md"
DATA_FILE = ROOT / "app" / "data" / "emails.json"


def read_architecture_doc() -> str:
    """Read the architecture document from the file system."""
    if not ARCHITECTURE_DOC.exists():
        return "Architecture document not found."
    
    try:
        return ARCHITECTURE_DOC.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading architecture document: {e}"


def send_architecture_email(recipient: str = "Swastik.Singh@gmail.com", sender: str = "pm@novamail.dev") -> dict:
    """
    Send the architecture document as an email.
    
    Args:
        recipient: Email address to send to
        sender: Email address to send from
    
    Returns:
        Dictionary with email details
    """
    from datetime import datetime, timezone
    
    # Read architecture document
    architecture_body = read_architecture_doc()
    
    # Load existing emails
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as f:
            emails = json.load(f)
    else:
        emails = []
    
    # Create new email
    next_id = max([e.get("id", 0) for e in emails], default=0) + 1
    email = {
        "id": next_id,
        "sender": sender,
        "recipient": recipient,
        "subject": "NovaMail POC Architecture Document — Complete",
        "body": architecture_body,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "email_type": "sent",
    }
    
    # Save email
    emails.append(email)
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(emails, f, indent=2)
    
    return email


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Send the NovaMail POC architecture document via email"
    )
    parser.add_argument(
        "--recipient",
        "-r",
        default="Swastik.Singh@gmail.com",
        help="Recipient email address (default: Swastik.Singh@gmail.com)",
    )
    parser.add_argument(
        "--sender",
        "-s",
        default="pm@novamail.dev",
        help="Sender email address (default: pm@novamail.dev)",
    )
    
    args = parser.parse_args()
    
    try:
        email = send_architecture_email(recipient=args.recipient, sender=args.sender)
        print(f"✓ Architecture email sent successfully!")
        print(f"  To: {email['recipient']}")
        print(f"  From: {email['sender']}")
        print(f"  Subject: {email['subject']}")
        print(f"  Email ID: {email['id']}")
        print(f"  Body length: {len(email['body'])} characters")
        return 0
    except Exception as e:
        print(f"✗ Error sending architecture email: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

