# Developer RCA: "Not Found" Image/Page Issue

## Reported Symptom
A blank gray page with only `Not Found` text appears instead of the NovaMail UI.

## Root Cause
The previous server routing accepted only `/` for the main page. Common entry paths in different environments such as `/index.html` or `/web/index.html` returned HTTP 404.

## Fix Implemented
1. Added route aliases for `/`, `/index.html`, and `/web/index.html`.
2. Added safe static path resolution to prevent bad path traversal and improve reliability.
3. Expanded MIME support to include common image types (`.png`, `.jpg`, `.svg`, `.ico`) so images are served correctly.

## Validation
- `GET /` returns 200.
- `GET /index.html` returns 200.
- `GET /web/index.html` returns 200.
- PM architecture email action now records a sent-simulated message to `Swastik.Singh@gmail.com`.
