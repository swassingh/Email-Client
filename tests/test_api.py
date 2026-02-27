import json
import os
import subprocess
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8010"


def req(path, method="GET", payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8")


def req_json(path, method="GET", payload=None):
    status, body = req(path, method=method, payload=payload)
    return status, json.loads(body)


def main():
    env = os.environ.copy()
    env["PORT"] = "8010"
    for key in ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "SMTP_FROM"]:
        env.pop(key, None)

    proc = subprocess.Popen(["python3", "app/server.py"], env=env)
    try:
        time.sleep(1)

        status, health = req_json("/api/health")
        assert status == 200 and health["status"] == "ok"

        status, _ = req("/")
        assert status == 200

        status, _ = req("/index.html")
        assert status == 200

        status, created = req_json(
            "/api/emails",
            method="POST",
            payload={
                "sender": "pm@novamail.dev",
                "recipient": "Swastik.Singh@gmail.com",
                "subject": "POC Architecture",
                "body": "Attached architecture summary.",
            },
        )
        assert status == 201
        assert created["id"] >= 1

        status, smtp_error = req_json(
            "/api/send-architecture-email",
            method="POST",
            payload={"recipient": "Swastik.Singh@gmail.com"},
        )
        assert status == 400
        assert "SMTP is not configured" in smtp_error["error"]

        status, inbox = req_json("/api/emails?recipient=Swastik.Singh@gmail.com")
        assert status == 200
        assert any(email["subject"] == "POC Architecture" for email in inbox)
        print("API checks passed")
    finally:
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    main()
