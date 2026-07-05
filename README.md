# ching-track     

> A full-stack personal finance tracker — log transactions, set budgets, track bills, manage savings goals, and gain insights into your spending. Built with Django REST Framework + React.

---

## Features

- **Transaction Tracking** — Log income and expenses with categorized breakdowns, monthly summaries, and filterable lists.
- **Budget Management** — Set monthly spending limits per category and track budget vs. actual spending with visual status indicators.
- **Recurring Bills** — Track recurring bills with due dates, payment history, and upcoming bill alerts.
- **Savings Goals** — Define savings targets with deadlines, log contributions, and track progress with on-track predictions.
- **Dashboard & Analytics** — Monthly snapshots, category spending breakdowns, budget alerts, upcoming bills, goal progress, and month-over-month trends.
- **M-Pesa Integration** — Parse M-Pesa SMS messages to auto-import transactions (Kenyan mobile money).
- **Multi-Currency Ready** — All monetary values support configurable currency codes (default: KES).
- **GDPR Compliance** — Export all your data or delete your account with a single click.
- **JWT Authentication** — Secure token-based auth with access/refresh token rotation and blacklisting.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python ≥3.13, Django ≥5.0, Django REST Framework ≥3.15 |
| **Auth** | JWT (djangorestframework-simplejwt) with rotation + blacklisting |
| **Database** | PostgreSQL 16 |
| **Frontend** | React 19, TypeScript 6, Vite 8, react-router-dom 7 |
| **API Docs** | drf-spectacular (Swagger UI + OpenAPI schema) |
| **Rate Limiting** | django-ratelimit |
| **CORS** | django-cors-headers |
| **Containerization** | Docker (PostgreSQL) |
| **Deployment** | Railway (backend) / Vercel (frontend) |

---

## Architecture

```
ching-track/
├── backend/                     # Django REST API
│   ├── config/settings/         # Split settings (base, development, production)
│   ├── apps/
│   │   ├── accounts/            # Auth, registration, email verification, GDPR
│   │   ├── transactions/        # Transactions & categories, M-Pesa parsing
│   │   ├── budgets/             # Budgets & user preferences
│   │   ├── bills/               # Recurring bills & payment tracking
│   │   ├── goals/               # Savings goals & contributions
│   │   └── analytics/           # Dashboard aggregation & trends
│   └── core/                    # Shared utilities (permissions, pagination, exceptions)
├── frontend/react/              # React SPA (Vite + TypeScript)
│   └── src/
│       ├── api/                 # Centralized API client with auto-refresh
│       ├── components/          # Layout, ProtectedRoute, shared UI
│       ├── pages/               # 15 route pages
│       ├── context/             # AuthContext (state management)
│       ├── types/               # TypeScript interfaces
│       └── utils/               # Helpers
├── docs/                        # PRD, implementation plans
├── docker-compose.yml           # PostgreSQL 16
└── pyproject.toml               # Root project config
```

### Design Decisions

- **API-first**: Django serves a pure REST API; the frontend is a fully separate SPA.
- **User-scoped data**: Every query filters by `user=request.user` with object-level `IsOwner` permissions.
- **Computed fields**: Budget spend, goal progress, bill due dates are computed at query time from source transactions.
- **Soft deletes**: Transactions (`is_deleted`) and bills (`is_active`) use soft delete for audit trails.
- **Decimal for money**: All monetary values use `DecimalField` — never floats.
- **No global state library**: Each page fetches its own data; avoids Redux/Zustand complexity for MVP.

---

## Prerequisites

- Python ≥ 3.13
- Node.js (with pnpm)
- Docker & Docker Compose
- PostgreSQL 16 (via Docker)

---

## Getting Started

### 1. Clone and configure

```bash
git clone <repository-url>
cd ching-track
cp .env.example .env
# Edit .env with your SECRET_KEY and other values
```

### 2. Start the database

```bash
docker compose up -d
```

This starts PostgreSQL 16 on port 5432.

### 3. Backend setup

```bash
# Create and activate virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements/development.txt

# Run migrations
python backend/manage.py migrate

# (Optional) Seed test data
python backend/manage.py shell -c "import seed; seed.run()"

# Start the dev server
python backend/manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`.

> **Test user** (after seeding): `test@chingtrack.com` / `Test1234!`

### 4. Frontend setup

```bash
cd frontend/react
pnpm install
pnpm run dev
```

The app will be available at `http://localhost:5173`.

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | (required) |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://chingtrack_user:chingtrack_pass@localhost:5432/chingtrack` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | CORS allowlist | `http://localhost:5173` |
| `FRONTEND_URL` | Frontend URL (for email links) | `http://localhost:5173` |
| `EMAIL_BACKEND` | Email backend | `django.core.mail.backends.console.EmailBackend` |

See `.env.example` for the full list.

---

## API Overview

All endpoints are prefixed with `/api/v1/`. Full interactive documentation is available at `/api/docs/` (Swagger UI) when the server is running.

| Resource | Endpoints |
|---|---|
| **Auth** | `register/`, `login/`, `logout/`, `token/refresh/`, `verify-email/<token>/`, `forgot-password/`, `reset-password/<token>/`, `change-password/`, `me/` |
| **GDPR** | `export-data/`, `delete-account/` |
| **Categories** | `GET/POST /categories/`, `GET/PUT/DELETE /categories/:id/` |
| **Transactions** | `GET/POST /transactions/`, `GET /transactions/summary/`, `GET/PUT/DELETE /transactions/:id/` |
| **Budgets** | `GET/POST /budgets/`, `GET /budgets/vs-actual/`, `DELETE /budgets/:id/` |
| **Preferences** | `GET/PUT /preferences/`, `GET /preferences/spending-status/` |
| **Bills** | `GET/POST /bills/`, `GET /bills/upcoming/`, `GET|PUT|DELETE /bills/:id/`, `POST /bills/:id/pay/` |
| **Goals** | `GET/POST /goals/`, `GET/PUT/DELETE /goals/:id/`, `POST /goals/:id/contribute/`, `GET /goals/:id/contributions/` |
| **Analytics** | `GET /analytics/dashboard/`, `GET /analytics/trends/` |
| **M-Pesa** | `POST /mpesa/parse-sms/`, `POST /mpesa/confirm-import/` |

---

## Deployment

### Backend (Railway)

```bash
DJANGO_SETTINGS_MODULE=config.settings.production python backend/manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

### Frontend (Vercel)

```bash
cd frontend/react
pnpm build  # Outputs to dist/
```

---

## Security

- JWT with rotation and refresh token blacklisting
- Rate limiting on all public auth endpoints (3–10 req/min per IP)
- Object-level `IsOwner` permissions on all detail views
- CSP headers, HSTS, Secure cookies, SSL redirect in production
- All monetary values stored as `DecimalField`
- Input validation on all fields
- User enumeration prevention on password reset


---

## Project Status

Actively developed. The current version is an MVP covering the core personal finance feature set. Planned enhancements include AI-powered insights, transaction auto-categorization, receipt scanning, and advanced reporting.

---


