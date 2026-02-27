To: Swastik.Singh@gmail.com
From: pm@novamail.dev
Subject: NovaMail POC Vision + Architecture for Manager Review

Hi Swastik,

As requested, here is the PM summary and architecture for the NovaMail proof of concept.

Vision:
NovaMail will become a modern email client focused on helping users process high-volume inboxes quickly with AI-assisted prioritization and summarization.

Architecture (POC):
1. Frontend: static HTML/CSS/JS UI with Compose and Inbox panels.
2. Backend: Python HTTP service with REST endpoints for health checks and email operations.
3. Storage: local JSON persistence for quick demo iteration.

Planned evolution after POC:
- Move persistence to PostgreSQL.
- Add authentication and mailbox access controls.
- Add async AI processing pipeline for summaries and action suggestions.

This is implementation-ready for the team to demo next week.

Best,
PM — NovaMail
