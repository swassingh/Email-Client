"""NovaMail POC — Streamlit UI. Shares the same email store as the HTTP server."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from app.store import DATA_FILE, EmailStore

# Path to architecture doc for "Send architecture email" demo
ROOT = Path(__file__).resolve().parent
ARCHITECTURE_DOC = ROOT / "docs" / "team" / "Team_Architecture.md"

DEFAULT_SENDER = "pm@novamail.dev"
VALID_TYPES = ["inbox", "sent", "draft", "scheduled", "spam", "junk", "trash"]


def get_store() -> EmailStore:
    return EmailStore(DATA_FILE)


def init_session_state() -> None:
    if "folder" not in st.session_state:
        st.session_state.folder = "inbox"
    if "selected_email_id" not in st.session_state:
        st.session_state.selected_email_id = None
    if "show_compose" not in st.session_state:
        st.session_state.show_compose = False


def infer_email_type(sender: str, explicit_type: str) -> str:
    if explicit_type and explicit_type.strip().lower() in VALID_TYPES:
        return explicit_type.strip().lower()
    if sender.strip().lower() == DEFAULT_SENDER.lower():
        return "sent"
    return "inbox"


def send_architecture_email(store: EmailStore) -> bool:
    """Create one email with the architecture doc body. Returns True on success."""
    if not ARCHITECTURE_DOC.exists():
        return False
    try:
        body = ARCHITECTURE_DOC.read_text(encoding="utf-8")
    except Exception:
        return False
    store.create(
        sender=DEFAULT_SENDER,
        recipient="Swastik.Singh@gmail.com",
        subject="NovaMail POC Architecture Document — Complete",
        body=body,
        email_type="sent",
    )
    return True


def main() -> None:
    st.set_page_config(page_title="NovaMail POC", page_icon="✉️", layout="wide")
    init_session_state()
    store = get_store()

    st.title("NovaMail POC")

    # Sidebar: folder selection and compose
    with st.sidebar:
        st.header("Folders")
        folder = st.radio(
            "Folder",
            options=["inbox", "sent", "draft", "scheduled", "spam", "junk", "trash", "all"],
            key="folder_radio",
            label_visibility="collapsed",
        )
        st.session_state.folder = folder

        if st.button("Compose", use_container_width=True):
            st.session_state.show_compose = True
            st.session_state.selected_email_id = None

        st.divider()
        if st.button("Send architecture email (demo)", use_container_width=True):
            if send_architecture_email(store):
                st.success("Architecture email added to Sent.")
            else:
                st.error("Could not read architecture document.")

    # Compose form (when show_compose)
    if st.session_state.show_compose:
        with st.expander("Compose Email", expanded=True):
            with st.form("compose_form"):
                sender = st.text_input("From", value=DEFAULT_SENDER)
                recipient = st.text_input("To", placeholder="Enter recipient email")
                subject = st.text_input("Subject", placeholder="Enter subject")
                body = st.text_area("Message", placeholder="Write your message...", height=200)
                schedule = st.checkbox("Schedule Send")
                scheduled_date = None
                scheduled_time = None
                if schedule:
                    col1, col2 = st.columns(2)
                    with col1:
                        scheduled_date = st.date_input("Date")
                    with col2:
                        scheduled_time = st.time_input("Time")

                col_send, col_draft, col_schedule, col_cancel = st.columns(4)
                with col_send:
                    submit_send = st.form_submit_button("Send")
                with col_draft:
                    submit_draft = st.form_submit_button("Save Draft")
                with col_schedule:
                    submit_schedule = st.form_submit_button("Schedule Send")
                with col_cancel:
                    submit_cancel = st.form_submit_button("Cancel")

                if submit_cancel:
                    st.session_state.show_compose = False
                    st.rerun()

                if submit_send:
                    if not (recipient and subject and body):
                        st.error("Please fill in To, Subject, and Message.")
                    else:
                        email_type = infer_email_type(sender, "")
                        store.create(
                            sender=sender.strip(),
                            recipient=recipient.strip(),
                            subject=subject.strip(),
                            body=body.strip(),
                            email_type=email_type,
                        )
                        st.success("Email sent.")
                        st.session_state.show_compose = False
                        st.rerun()

                if submit_draft:
                    if not (subject or body):
                        st.error("Please enter a subject or message to save as draft.")
                    else:
                        store.create(
                            sender=(sender or "").strip(),
                            recipient=(recipient or "").strip(),
                            subject=(subject or "").strip(),
                            body=(body or "").strip(),
                            email_type="draft",
                        )
                        st.success("Draft saved.")
                        st.session_state.show_compose = False
                        st.rerun()

                if submit_schedule:
                    if not (recipient and subject and body):
                        st.error("Please fill in To, Subject, and Message.")
                    elif not schedule or scheduled_date is None or scheduled_time is None:
                        st.error("Check Schedule Send and pick date and time.")
                    else:
                        combined = datetime.combine(scheduled_date, scheduled_time)
                        combined_utc = combined.replace(tzinfo=timezone.utc)
                        if combined_utc <= datetime.now(timezone.utc):
                            st.error("Scheduled time must be in the future.")
                        else:
                            store.create(
                                sender=sender.strip(),
                                recipient=recipient.strip(),
                                subject=subject.strip(),
                                body=body.strip(),
                                email_type="scheduled",
                                scheduled_at=combined_utc.isoformat(),
                            )
                            st.success(f"Email scheduled for {combined_utc.isoformat()}.")
                            st.session_state.show_compose = False
                            st.rerun()

        st.divider()

    # Main area: list and detail
    email_type_filter = None if st.session_state.folder == "all" else st.session_state.folder
    emails = store.list(email_type=email_type_filter)

    if not emails:
        st.info("No emails found.")
        st.session_state.selected_email_id = None
    else:
        # List: clickable rows
        for email in emails:
            etype = email.get("email_type", "inbox")
            is_sent = etype == "sent" or (email.get("sender", "").lower() == DEFAULT_SENDER.lower())
            other = email["recipient"] if is_sent else email["sender"]
            label = f"{email['subject']} — {other}"
            if st.button(
                label,
                key=f"list_{email['id']}",
                use_container_width=True,
            ):
                st.session_state.selected_email_id = email["id"]
                st.session_state.show_compose = False
                st.rerun()

        # Detail view
        if st.session_state.selected_email_id is not None:
            st.divider()
            email = store.get_by_id(st.session_state.selected_email_id)
            if email:
                st.subheader(email["subject"])
                st.caption(f"From: {email['sender']} | To: {email['recipient']}")
                st.caption(f"Date: {email['created_at']} | Type: {email.get('email_type', 'inbox')}")
                if email.get("scheduled_at"):
                    st.caption(f"Scheduled: {email['scheduled_at']}")
                st.text_area("Body", value=email["body"], height=200, disabled=True, key="detail_body")

                etype = (email.get("email_type") or "inbox").lower()
                is_sent = etype == "sent"

                col1, col2, col3, col4, col_back = st.columns(5)
                with col1:
                    if not is_sent and st.button("Move to Inbox", key="act_inbox"):
                        store.update_type(email["id"], "inbox")
                        st.session_state.selected_email_id = None
                        st.rerun()
                with col2:
                    if not is_sent and st.button("Mark as Spam", key="act_spam"):
                        store.update_type(email["id"], "spam")
                        st.session_state.selected_email_id = None
                        st.rerun()
                with col3:
                    if not is_sent and st.button("Mark as Junk", key="act_junk"):
                        store.update_type(email["id"], "junk")
                        st.session_state.selected_email_id = None
                        st.rerun()
                with col4:
                    if st.button("Move to Trash", key="act_trash"):
                        store.update_type(email["id"], "trash")
                        st.session_state.selected_email_id = None
                        st.rerun()
                with col_back:
                    if st.button("Back to list", key="back"):
                        st.session_state.selected_email_id = None
                        st.rerun()


if __name__ == "__main__":
    main()
