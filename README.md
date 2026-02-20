# Skills Assessment Platform Scaffold

Production-minded scaffold for a **WhatsApp + Web Skills Assessment** system with:

- **FastAPI** backend
- **PostgreSQL** (ACID-compliant transactional core)
- **Twilio WhatsApp webhook**
- **Real-time dashboard updates** (WebSocket)
- **Excel export**
- **React + Tailwind** modern admin UI
- **JWT auth + TOTP 2FA via QR code**

## Why this scaffold is ACID and best-practice aligned

1. **Atomicity**: each assessment submission is wrapped in one database transaction (`async with session.begin()`), so answers + scores + recommendations are committed together or rolled back together.
2. **Consistency**: foreign keys, check constraints, and unique constraints enforce valid data.
3. **Isolation**: transaction isolation can be tuned (`READ COMMITTED` default; promote critical writes to `REPEATABLE READ` / `SERIALIZABLE` where needed).
4. **Durability**: PostgreSQL WAL provides durable committed writes.

Additional software principles applied:
- Layered architecture (API → service → data)
- Single responsibility per module
- Twelve-factor configuration via `.env`
- Explicit migrations (Alembic)
- Idempotency token for submission safety
- Outbox event table for reliable async side-effects

---

## Quick Start (Docker)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Services:
- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

## Twilio + ngrok (dev)

1. Start stack.
2. Expose backend:
   ```bash
   ngrok http 8000
   ```
3. Configure Twilio WhatsApp sandbox webhook to:
   `https://<your-ngrok-domain>/api/v1/webhooks/twilio/whatsapp`
4. Put Twilio credentials in `backend/.env`.

---

## 2FA setup flow

1. User signs up and logs in.
2. Call `POST /api/v1/auth/2fa/setup` with access token.
3. Response includes QR image (`data:image/png;base64,...`) and secret.
4. User scans QR using authenticator app.
5. Verify with `POST /api/v1/auth/2fa/enable`.
6. Future logins require TOTP verification (`/auth/login` then `/auth/2fa/verify-login`).

---

## Core API summary

- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/2fa/setup`
- `POST /api/v1/auth/2fa/enable`
- `POST /api/v1/auth/2fa/verify-login`
- `GET /api/v1/questions`
- `POST /api/v1/questions` (admin)
- `POST /api/v1/assessments/submit`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/exports/assessments.xlsx`
- `POST /api/v1/webhooks/twilio/whatsapp`
- `WS /api/v1/ws/dashboard`

---

## Folder structure

```text
skills-assessment-scaffold/
  backend/
    app/
      api/v1/endpoints/
      core/
      models/
      schemas/
      services/
      tasks/
      utils/
      main.py
    alembic/
    requirements.txt
    Dockerfile
    .env.example
  frontend/
    src/
      components/
      pages/
      api/
    package.json
    Dockerfile
  docker-compose.yml
```

---

## Next steps after scaffold

1. Import your actual questionnaire into `questions` and `question_options` tables.
2. Add role-based permissions (super-admin, analyst, enumerator).
3. Add sector-level report endpoints and chart pages.
4. Add CI (lint, tests, security scans) and production hardening.
5. Replace dev secret handling with cloud KMS / vault.
