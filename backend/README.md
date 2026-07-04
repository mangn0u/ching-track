# ching-track Backend

Django REST API for the Personal Finance Tracker.

## Quick Start

```bash
# Set up virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements/development.txt

# Set up environment
cp .env.example .env  # then edit .env with your values

# Run database migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## Seed Data

```bash
python manage.py shell -c "import seed; seed.run()"
```

Test user: `test@chingtrack.com` / `Test1234!`

## API Documentation

Once running, visit `/api/docs/` for Swagger UI or `/api/schema/` for the OpenAPI schema.

## Apps

| App | Purpose |
|---|---|
| `accounts` | CustomUser, auth, email verification, password reset, GDPR |
| `transactions` | Transaction & Category CRUD, summary, M-Pesa parsing |
| `budgets` | Per-category budgets, global spending limit, vs-actual |
| `bills` | Recurring bills, payment tracking, upcoming bills |
| `goals` | Savings goals, contributions, progress tracking |
| `analytics` | Dashboard aggregation, multi-month trends |

## API Endpoints

All endpoints are prefixed with `/api/v1/` and require JWT authentication unless noted.

### Health
- `GET /api/v1/health/` — Health check (public)

### Auth (public endpoints: register, login, verify, forgot/reset password)
- `POST /api/v1/auth/register/`
- `GET /api/v1/auth/verify-email/<token>/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/token/refresh/`
- `POST /api/v1/auth/logout/`
- `GET|PUT /api/v1/auth/me/`
- `POST /api/v1/auth/change-password/`
- `POST /api/v1/auth/forgot-password/`
- `POST /api/v1/auth/reset-password/<token>/`
- `GET /api/v1/auth/export-data/` (GDPR)
- `DELETE /api/v1/auth/delete-account/` (GDPR)

### Transactions & Categories
- `GET|POST /api/v1/categories/`
- `GET|PUT|DELETE /api/v1/categories/:id/`
- `GET|POST /api/v1/transactions/`
- `GET /api/v1/transactions/summary/`
- `GET|PUT|PATCH|DELETE /api/v1/transactions/:id/`

### Budgets & Preferences
- `GET|POST /api/v1/budgets/`
- `GET /api/v1/budgets/vs-actual/`
- `DELETE /api/v1/budgets/:id/`
- `GET|PUT /api/v1/preferences/`
- `GET /api/v1/preferences/spending-status/`

### Bills
- `GET|POST /api/v1/bills/`
- `GET|PUT|DELETE /api/v1/bills/:id/`
- `POST /api/v1/bills/:id/pay/`
- `GET /api/v1/bills/upcoming/`

### Savings Goals
- `GET|POST /api/v1/goals/`
- `GET|PUT|DELETE /api/v1/goals/:id/`
- `POST /api/v1/goals/:id/contribute/`
- `GET /api/v1/goals/:id/contributions/`

### Analytics
- `GET /api/v1/analytics/dashboard/`
- `GET /api/v1/analytics/trends/`

### M-Pesa
- `POST /api/v1/mpesa/parse-sms/`
- `POST /api/v1/mpesa/confirm-import/`

## Deployment

```bash
# Production settings
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```
