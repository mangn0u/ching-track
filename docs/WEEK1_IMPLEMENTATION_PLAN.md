# Week 1 — Backend Implementation Plan
## ching-track Personal Finance Tracker

**Start:** Day 1, May 25, 2026
**Stack:** Django 5.x · DRF · PostgreSQL · JWT (SimpleJWT) · Railway
**Goal:** Fully tested REST API by end of Day 7. No frontend yet.

---

## Architecture Decisions (Locked)

| Decision | Choice | Rationale |
|---|---|---|
| Auth | JWT (SimpleJWT) | Stateless, mobile-ready, cross-domain |
| Multi-tenancy | User-scoped querysets everywhere | 1,000 independent users |
| Money | `DecimalField(max_digits=14, decimal_places=2)` | Never FloatField |
| Currency | `currency_code` CharField(3) on Transaction + UserPreferences | Multi-currency from Day 1 |
| Spending limit | Global `monthly_spending_limit` on UserPreferences | Option (b) as confirmed |
| M-Pesa | `mpesa_ref` + `mpesa_raw_sms` on Transaction | SMS parsing ready, no Daraja needed |
| Soft delete | `is_deleted=True` on Transaction | Audit trail |
| Compliance | Data export + account deletion endpoint | GDPR-style, Day 7 |
| Email | SMTP via SendGrid (free tier) | Verification + password reset in MVP |
| Rate limiting | `django-ratelimit` on auth endpoints | Brute force protection |

---

## Project Structure

```
ching-track/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/       # CustomUser, auth, email verification
│   │   ├── transactions/   # Transaction, Category
│   │   ├── budgets/        # Budget, UserPreferences (spending limit)
│   │   ├── bills/          # Bill, BillPayment
│   │   ├── goals/          # SavingsGoal, GoalContribution
│   │   └── analytics/      # Dashboard computed endpoint
│   ├── core/               # Base permissions, pagination, exceptions
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── manage.py
│   └── seed.py
├── docs/
├── .env.example
└── docker-compose.yml      # PostgreSQL local dev
```

---

## DAY 1 — Project Setup, Models & Migrations
**Deliverable:** `python manage.py migrate` runs clean. All models in DB.

### Tasks

**1. Environment & Scaffolding**
- Django project with split settings (`base`, `development`, `production`)
- `docker-compose.yml` for local PostgreSQL (avoids manual install)
- `.env.example` with all required keys

```
SECRET_KEY=
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/chingtrack
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid_key>
FRONTEND_URL=http://localhost:5173
```

**2. CustomUser Model (`accounts` app)**

```python
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True)
    mpesa_phone = models.CharField(max_length=15, blank=True, null=True)  # SMS parsing later
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
```

**3. UserPreferences Model**
```python
class UserPreferences(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, default='KES')
    monthly_spending_limit = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
```

**4. Transaction Model**
```python
class Transaction(models.Model):
    TYPES = [('income', 'Income'), ('expense', 'Expense')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=TYPES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency_code = models.CharField(max_length=3, default='KES')
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    mpesa_ref = models.CharField(max_length=20, blank=True)      # e.g. "RJK4X8Z..."
    mpesa_raw_sms = models.TextField(blank=True)                  # original SMS text
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**5. Other Models** (Category, Budget, Bill, BillPayment, SavingsGoal, GoalContribution) — follow PRD schema with these additions:
- All add `updated_at = DateTimeField(auto_now=True)`
- `SavingsGoal` adds `currency_code = CharField(max_length=3, default='KES')`

**Done when:** All tables exist in psql. Django admin loads. No migration errors.

---

## DAY 2 — Authentication + Email Verification
**Deliverable:** Register → verify email → login → JWT tokens working end-to-end.

### JWT Config
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Endpoints

| Method | Endpoint | Auth | Notes |
|---|---|---|---|
| POST | `/api/v1/auth/register/` | No | Creates user, sends verification email |
| GET | `/api/v1/auth/verify-email/<token>/` | No | Activates account |
| POST | `/api/v1/auth/login/` | No | Returns `{access, refresh, user}` |
| POST | `/api/v1/auth/token/refresh/` | No | Rotates tokens |
| POST | `/api/v1/auth/logout/` | Yes | Blacklists refresh token |
| GET/PUT | `/api/v1/auth/me/` | Yes | Profile view/update |
| POST | `/api/v1/auth/forgot-password/` | No | Sends reset email |
| POST | `/api/v1/auth/reset-password/<token>/` | No | Sets new password |
| POST | `/api/v1/auth/change-password/` | Yes | Old + new password |

### Security
- Rate limit login: 5 attempts/minute per IP
- Passwords: min 8 chars, 1 uppercase, 1 number
- Verification tokens: UUID, expire in 24h
- Passwords never returned in any serializer response

**Done when:** Full flow tested — register → email link → login → refresh → logout → blacklisted token rejected.

---

## DAY 3 — Transactions & Categories API
**Deliverable:** Full CRUD, month/year filter, summary endpoint.

### Auto-seed categories on user registration (via `post_save` signal)
```
Income:  Salary, Freelance, Business, Gift, M-Pesa Received, Other Income
Expense: Food, Transport, Housing, Utilities, Health,
         Entertainment, Shopping, Education, M-Pesa Sent, Other Expense
```

### Endpoints

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/categories/` | `?type=expense` |
| POST | `/api/v1/categories/` | Custom categories |
| PUT | `/api/v1/categories/:id/` | Block edit of default categories |
| DELETE | `/api/v1/categories/:id/` | Block if transactions linked |
| GET | `/api/v1/transactions/` | `?month=5&year=2026&type=expense&category=3&currency=KES` |
| POST | `/api/v1/transactions/` | Validates amount > 0, category belongs to user |
| GET | `/api/v1/transactions/:id/` | Detail |
| PUT/PATCH | `/api/v1/transactions/:id/` | Update |
| DELETE | `/api/v1/transactions/:id/` | Soft delete (is_deleted=True) |
| GET | `/api/v1/transactions/summary/` | `{income, expense, net, savings_rate, by_category[]}` |

### Summary Response Shape
```json
{
  "month": 5, "year": 2026, "currency": "KES",
  "total_income": "120000.00",
  "total_expense": "45000.00",
  "net": "75000.00",
  "savings_rate_pct": 62.5,
  "by_category": [
    {"category": "Food", "color": "#f43f5e", "amount": "12000.00", "pct": 26.7}
  ]
}
```

**Pagination:** 25 per page (cursor-based for scale).

**Done when:** CRUD tested. User A cannot see User B's data. Summary math correct.

---

## DAY 4 — Budget API + Global Spending Limit
**Deliverable:** Per-category budgets + global monthly limit — both with vs-actual.

### Endpoints

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/budgets/` | `?month=5&year=2026` |
| POST | `/api/v1/budgets/` | Upsert (create or update) |
| DELETE | `/api/v1/budgets/:id/` | Remove limit |
| GET | `/api/v1/budgets/vs-actual/` | Computed: limit vs real spend per category |
| GET/PUT | `/api/v1/preferences/` | View/update UserPreferences incl. spending limit |
| GET | `/api/v1/preferences/spending-status/` | Global limit vs current month total spend |

### vs-actual Response
```json
[
  {
    "category": "Food", "color": "#f43f5e",
    "limit": "15000.00", "actual": "12000.00",
    "remaining": "3000.00", "pct_used": 80.0,
    "status": "warning"
  }
]
```
> Status thresholds: `safe` = <80% | `warning` = 80-100% | `over` = >100%

### Spending Status Response
```json
{
  "monthly_limit": "80000.00",
  "total_spent": "45000.00",
  "remaining": "35000.00",
  "pct_used": 56.2,
  "status": "safe"
}
```

**Done when:** vs-actual correct. Over-limit status triggers correctly. Preferences save/load.

---

## DAY 5 — Bills API
**Deliverable:** CRUD bills, mark paid, upcoming bills view.

### Endpoints

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/bills/` | `?active=true` with `is_paid_this_period` computed |
| POST | `/api/v1/bills/` | Create recurring bill |
| PUT | `/api/v1/bills/:id/` | Edit |
| DELETE | `/api/v1/bills/:id/` | Soft delete (`is_active=False`) |
| POST | `/api/v1/bills/:id/pay/` | Creates BillPayment, blocks double-pay |
| GET | `/api/v1/bills/upcoming/` | Bills due in next 7 days |

**Pay endpoint logic:**
- Check if BillPayment already exists for current period → 400 if yes
- Create BillPayment record
- Optionally auto-create a matching expense Transaction

**Done when:** Lifecycle tested. Double-pay blocked. Upcoming filter correct.

---

## DAY 6 — Savings Goals API
**Deliverable:** CRUD goals, contribution log, progress + on-track computed.

### Endpoints

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/goals/` | With progress fields computed |
| POST | `/api/v1/goals/` | Create goal |
| GET/PUT/DELETE | `/api/v1/goals/:id/` | Detail |
| POST | `/api/v1/goals/:id/contribute/` | Add contribution |
| GET | `/api/v1/goals/:id/contributions/` | History (paginated) |

### Goal Response (computed fields)
```json
{
  "id": 1, "name": "Emergency Fund",
  "target_amount": "100000.00",
  "total_saved": "40000.00",
  "remaining": "60000.00",
  "progress_pct": 40.0,
  "days_remaining": 120,
  "monthly_required": "15000.00",
  "is_on_track": true,
  "currency_code": "KES"
}
```

**`is_on_track` logic:**
```
expected_saved = (days_elapsed / days_total) * target_amount
is_on_track = total_saved >= expected_saved
```

**Done when:** Progress math correct. `is_on_track` tested against edge cases (no deadline, goal met).

---

## DAY 7 — Dashboard Analytics, GDPR Endpoints & Security Audit
**Deliverable:** Single dashboard endpoint. Data export/delete. Hardened API. Seed script.

### Dashboard Endpoint
```
GET /api/v1/analytics/dashboard/?month=5&year=2026
```
Returns in one call:
- Monthly summary (income, expense, net, savings_rate)
- Spending by category
- Budget vs actual
- Global spending limit status
- Upcoming bills (next 7 days)
- Goals snapshot (name, progress_pct, is_on_track)
- Month-over-month change (income %, expense %)

### GDPR / Compliance Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/auth/export-data/` | Returns all user data as JSON |
| DELETE | `/api/v1/auth/delete-account/` | Hard deletes user + all data |

### Security Checklist
- [ ] All endpoints require `IsAuthenticated`
- [ ] No endpoint leaks another user's data (tested with 2 users)
- [ ] Auth endpoints rate-limited (5/min login)
- [ ] Passwords never in any response
- [ ] `DEBUG=False` tested in production settings
- [ ] `SECRET_KEY` from env only
- [ ] `SECURE_BROWSER_XSS_FILTER = True`
- [ ] `X_FRAME_OPTIONS = 'DENY'`
- [ ] `SECURE_CONTENT_TYPE_NOSNIFF = True`
- [ ] Amount always > 0 validated
- [ ] `due_day` in 1-31 validated
- [ ] `month` in 1-12 validated

### Seed Script (`seed.py`)
- 1 test user: `test@chingtrack.com` / `Test1234!`
- 10 categories (mix income/expense)
- 90 days of transactions (3 months, ~20/month, multi-currency mix)
- Budgets for current + last month
- 2 active bills
- 1 savings goal with contribution history

### Final Steps
- [ ] `python manage.py spectacular --file schema.yml` (OpenAPI docs)
- [ ] Run seed, verify all endpoints
- [ ] Write `backend/README.md`
- [ ] `git commit -m "feat: complete Week 1 backend"`

**Done when:** Security checklist 100%. Seed works. All endpoints documented.

---

## Full API Surface (End of Week 1)

```
/api/v1/
├── auth/
│   ├── register/                POST
│   ├── verify-email/<token>/    GET
│   ├── login/                   POST
│   ├── token/refresh/           POST
│   ├── logout/                  POST
│   ├── me/                      GET, PUT
│   ├── change-password/         POST
│   ├── forgot-password/         POST
│   ├── reset-password/<token>/  POST
│   ├── export-data/             GET    (GDPR)
│   └── delete-account/          DELETE (GDPR)
├── preferences/                 GET, PUT
│   └── spending-status/         GET
├── categories/                  GET, POST
│   └── :id/                     PUT, DELETE
├── transactions/                GET, POST
│   ├── summary/                 GET
│   └── :id/                     GET, PUT, PATCH, DELETE
├── budgets/                     GET, POST
│   ├── vs-actual/               GET
│   └── :id/                     DELETE
├── bills/                       GET, POST
│   ├── upcoming/                GET
│   └── :id/
│       ├── (detail)             GET, PUT, DELETE
│       └── pay/                 POST
├── goals/                       GET, POST
│   └── :id/
│       ├── (detail)             GET, PUT, DELETE
│       ├── contribute/          POST
│       └── contributions/       GET
└── analytics/
    └── dashboard/               GET
```

---

## Requirements

```txt
# requirements/base.txt
django>=5.0
djangorestframework>=3.15
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.3
psycopg2-binary>=2.9
python-decouple>=3.8
django-ratelimit>=4.1
drf-spectacular>=0.27
django-extensions>=3.2
Faker>=24.0
```

---

## Week 1 Risk Log

| Risk | Mitigation |
|---|---|
| JWT blacklist grows at scale | Schedule `flushexpiredtokens` weekly |
| Missing user scope on a queryset | `core/` base ViewSet forces `user=request.user` |
| Multi-currency conversion complexity | Store raw amounts in original currency. No conversion in MVP. |
| Email delivery in dev | Use `django.core.mail.backends.console.EmailBackend` in development.py |
| Schema change after Day 3 | Schema finalized EOD 1. Freeze after Day 2 migrations. |
