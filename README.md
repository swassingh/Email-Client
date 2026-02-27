# NovaMail POC (Email-Client)

NovaMail is a redesigned email-client POC with a modern UX and an outcome-first inbox.

## Team of 4 Deliverables
- PM Vision: `docs/team/PM_Vision.md`
- Team Lead Architecture: `docs/team/Team_Architecture.md`
- UX + Backend Execution: `docs/team/Developer_Execution.md`
- PM Draft Email: `docs/communications/PM_email_to_Swastik_Singh.md`

## Run locally
```bash
python3 app/server.py
```
Open:
- `http://localhost:8000/`
- `http://localhost:8000/index.html`

## Real SMTP email delivery (to Gmail inbox)
`POST /api/send-architecture-email` now performs real SMTP send.
Set these variables before starting server:

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your.account@gmail.com"
export SMTP_PASS="your_app_password"
export SMTP_FROM="your.account@gmail.com"
export SMTP_USE_TLS="true"
export SMTP_USE_SSL="false"
python3 app/server.py
```

Then click **Send PM Architecture Email** in the UI.

> Gmail note: use an App Password (not your main password).

## API
- `GET /api/health`
- `GET /api/emails?recipient=<email>`
- `POST /api/emails`
- `POST /api/send-architecture-email`
