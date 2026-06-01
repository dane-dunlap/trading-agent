"""Optional email digest functionality for the trading agent.

Sends a plain-text email via SMTP. Configure these env vars in .env to enable:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, NOTIFY_FROM, NOTIFY_TO

If SMTP is not configured, the message is simply printed to stdout so the
routine never fails just because email isn't set up.

Usage:
    python3 scripts/notify.py "subject" "body text"
"""
import os
import sys
import smtplib
from email.message import EmailMessage


def send(subject, body):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("NOTIFY_FROM", user)
    recipient = os.getenv("NOTIFY_TO")

    if not (host and user and password and recipient):
        print("[notify] SMTP not configured; printing instead:\n")
        print(f"Subject: {subject}\n\n{body}")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
    print(f"[notify] sent '{subject}' to {recipient}")


if __name__ == "__main__":
    subject = sys.argv[1] if len(sys.argv) > 1 else "Trading Agent Digest"
    body = sys.argv[2] if len(sys.argv) > 2 else ""
    send(subject, body)
