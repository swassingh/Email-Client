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

## Run with Streamlit
You can run the same email client as a Streamlit app (same data in `app/data/emails.json`):

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   streamlit run streamlit_app.py
   ```
3. Open the URL shown in the terminal (e.g. http://localhost:8501).

The original web app (`python app/server.py`) still serves the HTML/JS UI on port 8000.

## Deploy on Streamlit Community Cloud
Push the repo to GitHub, then at [share.streamlit.io](https://share.streamlit.io): New app → connect the repo, set **Main file path** to `streamlit_app.py`, and deploy. Note: on Streamlit Cloud the filesystem is ephemeral, so email data will not persist across redeploys unless you switch to a database or external storage.

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
