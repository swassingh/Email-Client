# Team Lead Architecture — NovaMail POC

## System Overview
A lightweight single-service architecture to accelerate prototyping:
- **Presentation layer**: static HTML/CSS/JS frontend.
- **API layer**: Python HTTP server exposing `/api/health` and `/api/emails`.
- **Persistence layer**: JSON file (`app/data/emails.json`) for simple local durability.

## Why this architecture
- Minimal dependencies for rapid setup.
- Easy to evolve into service-oriented design (auth, notifications, AI inference) after POC.
- Clear ownership boundaries for UX and backend roles.

## API Contracts
- `GET /api/health` → service status.
- `GET /api/emails?recipient=` → list messages filtered by recipient.
- `POST /api/emails` → validate and create email payload.

## Future scale path
1. Replace JSON file store with PostgreSQL.
2. Add authentication and mailbox ownership checks.
3. Add async job queue for AI summarization.
4. Split into frontend SPA + backend API gateway.
