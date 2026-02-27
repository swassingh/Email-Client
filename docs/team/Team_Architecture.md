# Team Lead Architecture — NovaMail POC v2

## North-Star Architecture
NovaMail is rebuilt around an **Outcome Inbox Architecture**:
1. **Capture Layer**: compose + ingestion APIs accept incoming/outgoing messages.
2. **Intelligence Layer (POC rules, future AI)**: classifies each message into Focus Now, Quick Wins, or FYI Stream.
3. **Experience Layer**: triage lanes drive decisions instead of linear message lists.
4. **Delivery Layer**: SMTP service sends external messages (including Gmail) using provider credentials.

## POC Components
- Frontend: static web app (`web/`) with modern lane-based inbox rendering.
- Backend: Python HTTP API (`app/server.py`) exposing:
  - `GET /api/health`
  - `GET /api/emails?recipient=`
  - `POST /api/emails`
  - `POST /api/send-architecture-email` (SMTP send)
- Persistence: local JSON data store for deterministic demos.

## External Email Delivery
SMTP integration requires:
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `SMTP_FROM`
Optional:
- `SMTP_USE_TLS=true|false`
- `SMTP_USE_SSL=true|false`

For Gmail, use an App Password and provider SMTP settings.

## Scale Path
- Replace JSON with PostgreSQL + migration pipeline.
- Add identity + tenant-safe mailbox boundaries.
- Introduce event bus and async AI scoring/summarization workers.
- Add conversation threading + action suggestions.
