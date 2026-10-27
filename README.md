# Panther OSINT

A privacy-first Flask self-audit website. Email ownership verification, security links for checking Google connected apps, saved logins, device sessions, and public breach exposure.

## Limitations
This application cannot reveal all websites where a particular email is registered or all current sessions. It does not enumerate third-party accounts. An email must be owned and verified. SMTP must be configured to enable email verification. Verification challenges use in-memory storage, so production scaling and durable rate limiting require Redis or a database.

## Local setup

```bash
pip install -r requirements.txt
python app.py
```

Set environment variables SMTP_HOST, SMTP_PORT (465 by default), SMTP_USER, SMTP_PASSWORD, SMTP_FROM, SECRET_KEY, PRODUCTION=1 for live OTP. Never commit credentials. Use a single Gunicorn worker with the current temporary in-memory implementation.

## Deploy
Connect this repository to Render as a Python Web Service; build command: `pip install -r requirements.txt`; start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1`.
