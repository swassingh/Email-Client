# NovaMail POC (Email-Client)

Proof-of-concept email client prepared for a manager demo.

## Team of 4
- PM: Vision and stakeholder communication.
- Team Lead: Architecture.
- UX Developer: Web client experience.
- Backend Designer: API and persistence.

Artifacts:
- PM vision: `docs/team/PM_Vision.md`
- Architecture: `docs/team/Team_Architecture.md`
- Developer split: `docs/team/Developer_Execution.md`
- PM email draft to stakeholder: `docs/communications/PM_email_to_Swastik_Singh.md`
- Developer RCA for Not Found issue: `docs/team/Developer_Image_Issue_RCA.md`

## Run on your local machine
### 1) Requirements
- Python 3.10+ installed

### 2) Start the app
```bash
cd Email-Client
python3 app/server.py
```

You should see:
```text
POC Email Client server listening on http://0.0.0.0:8000
```

### 3) Open in browser
Use either:
- `http://localhost:8000/`
- `http://localhost:8000/index.html`

## Troubleshooting: preview says "Not Found"
If you still see a blank `Not Found` page/image in a preview tool:
1. Confirm you are opening the app URL (not a stale preview URL):
   - `http://localhost:8000/index.html`
2. Confirm server is running in your terminal.
3. Verify routes manually:
   ```bash
   curl -i http://localhost:8000/
   curl -i http://localhost:8000/index.html
   curl -i http://localhost:8000/web/index.html
   ```
   All should return `HTTP/1.0 200 OK`.
4. If port 8000 is busy, run:
   ```bash
   PORT=8123 python3 app/server.py
   ```
   then open `http://localhost:8123/index.html`.

## API
- `GET /api/health`
- `GET /api/emails?recipient=<email>`
- `POST /api/emails`
- `POST /api/send-architecture-email`
