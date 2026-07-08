# Product Requirements Document
## ching-track — Personal Finance Tracker

**Version:** 2.0  
**Owner:** Mang'nu  
**Stack:** Python 3.13+ · Django 6.0 · Django REST Framework 3.17 · PostgreSQL 16 · React 19 · TypeScript 6 · Vite 8  
**Deployment:** Railway (backend) + Vercel (frontend)  
**Status:** Built — MVP complete with extended features

---

## 1. Problem Statement

### Why Does This Exist?

We live in a world where most of us operate without a system for tracking income, spending, and savings goals consistently make decisions in an information vacuum. The result is lifestyle inflation, surprise bills, and savings that never compound. The problem is not willpower — it is architecture. You need a single source of truth that shows you where money is going in real time.

### What Problem Does It Solve?

| Symptom | Root Cause | This Tool Fixes |
|---|---|---|
| "I don't know where my money went" | No transaction log | Transaction entry + category drill-down |
| "I forgot that bill was due" | No bill calendar | Bill tracker with due dates + upcoming bills |
| "I never hit my savings targets" | No visible goal progress | Savings goals with progress bars + on-track prediction |
| "My budget is just a spreadsheet guess" | No feedback loop | Budget vs actuals per category with color-coded status |
| "Manual entry is tedious" | No import from mobile money | M-Pesa SMS parsing → auto-create transactions |

### Key Design Constraints

- **Solo-built** → No microservices. One Django app, one React SPA.
- **No external bank APIs** → No Plaid/Plaid-like connections. Manual entry + M-Pesa SMS parsing.
- **Multi-currency ready** → `currency_code` on every monetary model. No conversion in current version.
- **Row-level isolation** → Every query scoped to `user=request.user` with `IsOwner` permissions.

---

## 2. Feature Overview

### 2.1 Authentication & Account Management

| Feature | Status |
|---|---|
| Email-based registration with email verification (24h token) | ✓ |
| JWT login with access (60min) + refresh (7d) token rotation | ✓ |
| Refresh token blacklisting on logout | ✓ |
| Password reset flow (forgot/reset with 1h token) | ✓ |
| Change password (authenticated) | ✓ |
| Profile view/edit (first name, last name, phone, M-Pesa phone) | ✓ |
| Rate limiting on all public auth endpoints (3–10 req/min/IP) | ✓ |

### 2.2 Transaction Management

| Feature | Status |
|---|---|
| Create, read, update, delete income & expense transactions | ✓ |
| Filter by month, year, type, category, currency | ✓ |
| Running balance (cumulative income − expenses) | ✓ |
| Monthly summary (income, expense, net, savings rate, by-category breakdown) | ✓ |
| Soft delete with audit trail (`is_deleted` flag) | ✓ |
| M-Pesa reference and raw SMS storage fields | ✓ |

### 2.3 Category System

| Feature | Status |
|---|---|
| 16 system-seeded default categories (6 income, 10 expense) with emoji icons | ✓ |
| Custom category creation with color + icon | ✓ |
| Type tabs (income / expense) in frontend | ✓ |
| Default categories protected from edit/delete | ✓ |
| Delete blocked when linked transactions exist | ✓ |

### 2.4 Budget Management

| Feature | Status |
|---|---|
| Per-category monthly budget with upsert logic | ✓ |
| Budget vs actual computation per category | ✓ |
| Status badges (safe / warning / over) with color coding | ✓ |
| Global monthly spending limit (e.g. KES 80,000) | ✓ |
| Spending limit status (total spent, remaining, percentage used) | ✓ |

### 2.5 Bill Tracking

| Feature | Status |
|---|---|
| Recurring bills (monthly, weekly, one-time) with due dates | ✓ |
| Soft deactivate (set `is_active=False`) | ✓ |
| Pay bill → creates BillPayment + auto-creates expense Transaction | ✓ |
| Computed next due date per bill | ✓ |
| Paid-this-period checking | ✓ |
| Upcoming bills (next 7 days) endpoint | ✓ |

### 2.6 Savings Goals

| Feature | Status |
|---|---|
| Goals with name, description, target amount, deadline | ✓ |
| Contribution logging with history view | ✓ |
| Computed fields: total_saved, remaining, progress_pct | ✓ |
| Days remaining, monthly_required, is_on_track (pace-based) | ✓ |
| On-track prediction comparing elapsed time vs saved amount | ✓ |

### 2.7 Dashboard & Analytics

| Feature | Status |
|---|---|
| Single-request dashboard: summary + category breakdown + budget vs actual + global limit + upcoming bills + goals + MoM changes | ✓ |
| Multi-month trends (3 / 6 / 12 month range) | ✓ |
| Top spending categories over any period | ✓ |
| Month-over-month change indicators | ✓ |

### 2.8 M-Pesa SMS Parsing

| Feature | Status |
|---|---|
| Regex-based parser for standard M-Pesa SMS formats | ✓ |
| Extracts: amount, type (send/receive), reference code, counterparty name, date | ✓ |
| XSS sanitization on parsed fields | ✓ |
| Parse → preview → confirm import flow | ✓ |
| Duplicate M-Pesa reference detection | ✓ |
| 29 unit tests covering all supported SMS formats | ✓ |

### 2.9 GDPR & Data Privacy

| Feature | Status |
|---|---|
| Export all user data as JSON (profile, categories, transactions, budgets, preferences, bills, goals) | ✓ |
| Delete account with full cascade (hard delete) | ✓ |

### 2.10 Reports

| Feature | Status |
|---|---|
| Interactive multi-month trend chart | ✓ |
| Monthly breakdown table with income/expense/net | ✓ |
| Top spending categories ranked | ✓ |

### 2.11 Settings

| Feature | Status |
|---|---|
| Profile editing | ✓ |
| Preferences: currency, monthly spending limit | ✓ |
| GDPR data export + account deletion | ✓ |
| Change password | ✓ |

---

## 3. User Stories

| ID | Story | Acceptance Criteria |
|---|---|---|
| U1 | As a user, I can register with email and verify my account | Registration sends verification email; 24h token must be clicked to activate |
| U2 | As a user, I can log in and have my data be private | Login with email + password returns JWT; unauthenticated requests return 401 |
| U3 | As a user, I can add a transaction with amount, category, date, note | Form validates: amount > 0, category required, date required |
| U4 | As a user, I can see all transactions in a list, filterable by month | Default view = current month; filter by prev months, type, category |
| U5 | As a user, I can see my running balance alongside transactions | Running balance column shows cumulative net after each transaction |
| U6 | As a user, I can edit or delete any transaction | Changes reflect immediately in totals |
| U7 | As a user, I can see my spending breakdown by category this month | Dashboard bar chart: category vs amount spent |
| U8 | As a user, I can set a monthly budget for each category | Input per category; limits color-coded (green/yellow/red) in dashboard |
| U9 | As a user, I can set a global monthly spending limit | Single ceiling across all expenses; remaining amount shown |
| U10 | As a user, I can add a bill with name, amount, due date, recurrence | Fields: name, amount, due_day (1-31), frequency (monthly/weekly/once) |
| U11 | As a user, I can mark a bill as paid and have an expense transaction created | Pay button creates BillPayment + Transaction record |
| U12 | As a user, I can see bills due in the next 7 days | Dashboard shows upcoming bills with pay buttons |
| U13 | As a user, I can create a savings goal with a name, target, deadline | Progress bar = contributions / target |
| U14 | As a user, I can log a contribution to a savings goal | Contribution history shows per goal with date and note |
| U15 | As a user, I can see if I'm on track to meet my savings goal | On-track indicator compares elapsed time vs saved amount |
| U16 | As a user, I can manage my categories (add, edit, delete custom ones) | Separate page with income/expense tabs; defaults protected |
| U17 | As a user, I can import transactions from M-Pesa SMS | Paste SMS text → preview parsed transaction → confirm to create |
| U18 | As a user, I can view multi-month trends and top spending categories | Reports page with 3/6/12 month range selector and chart |
| U19 | As a user, I can export all my data as JSON | Single-click GDPR data export |
| U20 | As a user, I can delete my account and all associated data | Account deletion with full cascade |
| U21 | As a user, I can change my password | Requires old password; validates new password complexity |
| U22 | As a user, I can reset my password if I forgot it | Email with 1h token; rate-limited to prevent enumeration |

---

## 4. Data Architecture

> **First Principles:** The data model is the contract between frontend and backend. All monetary values use `DecimalField` — never floats. All dates use `DateField` (not `DateTimeField`) to avoid timezone bugs.

### 4.1 Entity-Relationship Diagram

```
CustomUser (email as username, no username field)
  │
  ├── EmailVerificationToken (1:1, 24h expiry)
  │
  ├── PasswordResetToken (1:N, 1h expiry)
  │
  ├── UserPreferences (1:1, currency, monthly_spending_limit)
  │
  ├── Category (name, type: income|expense, color, icon, is_default)
  │
  ├── Transaction (amount, type, category, date, currency, note,
  │   │            mpesa_ref, mpesa_raw_sms, is_deleted)
  │   │
  │   └── Budget (category, month, year, limit_amount)
  │
  ├── Bill (name, amount, due_day, currency, frequency, is_active)
  │   └── BillPayment (bill, paid_date, amount_paid, note)
  │
  └── SavingsGoal (name, description, target_amount, currency, deadline)
      └── GoalContribution (goal, amount, date, note)
```

### 4.2 Database Models

#### `accounts.CustomUser`
- Email-based auth: `email` (unique, USERNAME_FIELD), `first_name`, `last_name`
- `phone_number`, `mpesa_phone` (for future Daraja API)
- `is_email_verified` (must be true before login)
- Managed by `CustomUserManager` (no username field)
- Signals: on creation → auto-creates `UserPreferences` + 16 default `Category` entries

#### `accounts.EmailVerificationToken`
- One-to-one with user, UUID token, 24-hour TTL (`expires_at`)

#### `accounts.PasswordResetToken`
- ForeignKey to user (multiple resets allowed), UUID token, 1-hour TTL
- `is_used` flag (one-time use)

#### `transactions.Category`
- `user` (FK), `name`, `type` (income/expense), `color` (hex), `icon` (emoji), `is_default`
- `unique_together = (user, name, type)`

#### `transactions.Transaction`
- `user` (FK), `category` (FK, SET_NULL on delete)
- `type`, `amount` (Decimal 14,2), `currency_code` (default KES)
- `date`, `note`, `mpesa_ref`, `mpesa_raw_sms`
- `is_deleted` (soft delete — never hard-deleted)
- Indexes: `(user, date)`, `(user, type)`, `(user, is_deleted)`

#### `budgets.UserPreferences`
- One-to-one with user, `currency`, `monthly_spending_limit` (nullable Decimal)
- Auto-created via signal on registration

#### `budgets.Budget`
- `user` (FK), `category` (FK), `month`, `year`, `limit_amount`
- `unique_together = (user, category, month, year)` — upsert logic in view

#### `bills.Bill`
- `user` (FK), `name`, `amount` (Decimal 14,2), `currency_code`, `due_day` (1-31)
- `frequency` (monthly/weekly/once), `is_active` (soft delete)

#### `bills.BillPayment`
- `bill` (FK), `paid_date`, `amount_paid`, `note`
- One record per billing period per bill

#### `goals.SavingsGoal`
- `user` (FK), `name`, `description`, `target_amount`, `currency_code`
- `deadline` (nullable)
- Property: `total_saved` = SUM of contributions (computed at query time)
- Serializer computed fields: `total_saved`, `remaining`, `progress_pct`, `days_remaining`, `monthly_required`, `is_on_track`

#### `goals.GoalContribution`
- `goal` (FK), `amount`, `date`, `note`

---

## 5. API Design

> All endpoints prefixed `/api/v1/`. Authentication via JWT Bearer token. Full OpenAPI schema at `/api/schema/`, Swagger UI at `/api/docs/`.

### 5.1 Health

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/health/` | Public | Health check → `{"status":"ok"}` |

### 5.2 Auth

| Method | Endpoint | Rate Limit | Description |
|---|---|---|---|
| POST | `/auth/register/` | 3/min/IP | Create account + send verification email |
| GET | `/auth/verify-email/<uuid:token>/` | 10/min/IP | Activate account |
| POST | `/auth/login/` | 5/min/IP | Login → `{access, refresh, user}` |
| POST | `/auth/token/refresh/` | — | Rotate access token |
| POST | `/auth/logout/` | — | Blacklist refresh token |
| GET/PUT | `/auth/me/` | — | View / update profile |
| POST | `/auth/change-password/` | — | Change password (requires old password) |
| POST | `/auth/forgot-password/` | 3/min/IP | Send reset email (enumeration-safe) |
| POST | `/auth/reset-password/<uuid:token>/` | 5/min/IP | Set new password with token |
| GET | `/auth/export-data/` | — | GDPR: export all user data as JSON |
| DELETE | `/auth/delete-account/` | — | GDPR: hard delete account + all data |

### 5.3 Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/categories/` | List (`?type=income`/`expense`) |
| POST | `/categories/` | Create custom category |
| GET/PUT/DELETE | `/categories/:id/` | Retrieve / update (non-default) / delete |

### 5.4 Transactions

| Method | Endpoint | Description |
|---|---|---|
| GET | `/transactions/` | List (paginated, filters: `?month`, `?year`, `?type`, `?category`, `?currency`) |
| POST | `/transactions/` | Create |
| GET | `/transactions/summary/` | Monthly totals: income, expense, net, savings_rate, by_category |
| GET/PUT/PATCH/DELETE | `/transactions/:id/` | Retrieve / update / partial update / soft-delete |

### 5.5 Budgets

| Method | Endpoint | Description |
|---|---|---|
| GET | `/budgets/` | List (`?month`, `?year`) |
| POST | `/budgets/` | Upsert (create or update) |
| GET | `/budgets/vs-actual/` | Budget vs actual per category with safe/warning/over status |
| DELETE | `/budgets/:id/` | Delete budget |

### 5.6 Preferences

| Method | Endpoint | Description |
|---|---|---|
| GET/PUT | `/preferences/` | View / edit currency, monthly_spending_limit |
| GET | `/preferences/spending-status/` | Global limit: total_spent, remaining, pct_used, status |

### 5.7 Bills

| Method | Endpoint | Description |
|---|---|---|
| GET | `/bills/` | List (`?active=true/false`) |
| POST | `/bills/` | Create |
| GET | `/bills/upcoming/` | Bills due in next 7 days |
| GET/PUT/DELETE | `/bills/:id/` | Retrieve / update / soft-delete |
| POST | `/bills/:id/pay/` | Pay → creates BillPayment + expense Transaction |

### 5.8 Savings Goals

| Method | Endpoint | Description |
|---|---|---|
| GET | `/goals/` | List with computed progress fields |
| POST | `/goals/` | Create |
| GET/PUT/DELETE | `/goals/:id/` | Retrieve / update / delete |
| POST | `/goals/:id/contribute/` | Add contribution |
| GET | `/goals/:id/contributions/` | Contribution history |

### 5.9 Analytics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/dashboard/` | Full dashboard: summary, category breakdown, budget vs actual, global limit, upcoming bills, goals, MoM change |
| GET | `/analytics/trends/` | Multi-month trends (3/6/12 months) + top categories |

### 5.10 M-Pesa

| Method | Endpoint | Description |
|---|---|---|
| POST | `/mpesa/parse-sms/` | Parse raw M-Pesa SMS → pre-filled transaction preview |
| POST | `/mpesa/confirm-import/` | Confirm and create transaction from parsed data |

---

## 6. Frontend Architecture

### 6.1 Pages & Routes

| Route | Page | Auth | Description |
|---|---|---|---|
| `/login` | `Login.tsx` | No | Sign in |
| `/register` | `Register.tsx` | No | Registration (name, email, password, phone) |
| `/forgot-password` | `ForgotPassword.tsx` | No | Enter email for reset link |
| `/reset-password/:token` | `ResetPassword.tsx` | No | Set new password |
| `/verify-email/:token` | `VerifyEmail.tsx` | No | Verification status |
| `/` | `Dashboard.tsx` | Yes | Summary cards, category chart, budget vs actual, upcoming bills, goals, MoM change |
| `/transactions` | `Transactions.tsx` | Yes | Filtered list, CRUD modals, running balance, detail modal |
| `/budgets` | `Budgets.tsx` | Yes | Budget list with vs-actual, status badges, CRUD modal |
| `/bills` | `Bills.tsx` | Yes | Bill cards, pay button, CRUD modal |
| `/goals` | `Goals.tsx` | Yes | Goal cards, progress bars, contribute modal, history modal |
| `/categories` | `Categories.tsx` | Yes | Category list with income/expense tabs, CRUD modal |
| `/mpesa-import` | `MpesaImport.tsx` | Yes | Paste SMS → parse → preview → import |
| `/reports` | `Reports.tsx` | Yes | Multi-month trend chart, monthly breakdown, top categories |
| `/settings` | `Settings.tsx` | Yes | Profile, preferences, GDPR export, delete account |
| `/change-password` | `ChangePassword.tsx` | Yes | Change password form |

### 6.2 Component Tree

```
App
├── AuthProvider (Context: user, tokens, login, logout)
├── Layout
│   ├── Sidebar (all nav links, user avatar, month/year, logout)
│   └── <Outlet /> (react-router)
├── ProtectedRoute (redirects to /login if unauthenticated)
├── Pages (see above)
└── Shared Components
    ├── Icons (EditIcon, DeleteIcon, CloseIcon, ViewIcon, HistoryIcon)
    └── format.ts (Intl.NumberFormat currency formatting)
```

### 6.3 State Management

- **Auth state:** React Context (`AuthContext`) — user object, tokens, login/logout functions
- **API client:** Centralized `client.ts` with JWT auto-refresh, `setTokens`/`clearTokens`
- **Server data:** Each page fetches its own data via `useEffect` + local `useState`
- **Forms:** Controlled components with local `useState`
- **No Redux/Zustand** — each page is self-contained

### 6.4 API Service Modules

| Module | Key Functions |
|---|---|
| `auth.ts` | Login, register, forgot/reset password, change password, profile CRUD, export data, delete account, verify email, logout |
| `categories.ts` | Fetch, create, update, delete categories |
| `transactions.ts` | Fetch (filtered), create, update, delete, fetch detail, fetch summary |
| `budgets.ts` | Fetch, upsert, delete, fetch vs-actual |
| `bills.ts` | Fetch, create, update, delete, pay bill |
| `goals.ts` | Fetch, create, update, delete, contribute, fetch contributions |
| `mpesa.ts` | Parse SMS, confirm import |
| `dashboard.ts` | Fetch dashboard data |
| `reports.ts` | Fetch trends data |
| `preferences.ts` | Fetch, update preferences, fetch spending status |

---

## 7. UI/UX Design

### 7.1 Design System

- **Theme:** Dark editorial — backgrounds `#0f0f0f`, surfaces `#1a1a1a`, borders `#2a2a2a`
- **Typography:** System font stack
- **Colors:**
  - Income: cyan `#22d3ee`
  - Expense: rose `#f43f5e`
  - Accent (brand): purple `#6366f1`
  - Muted text: `#6b7280`
  - Budget safe: emerald, Budget warning: amber, Budget over: rose
- **Key principle:** Numbers always right-aligned. Income always cyan. Expense always rose.

### 7.2 Dashboard Layout

```
┌────────────────────────────────────────────┐
│  June 2026            [< prev]  [next >]   │
├──────────┬──────────┬──────────┬───────────┤
│ Income   │ Expenses │   Net    │ Saved     │
│ +120,000 │ -45,000  │ +75,000  │ 20,000    │
├──────────┴──────────┴──────────┴───────────┤
│ Spending by Category     Budget vs Actual  │
│ [horizontal bar chart]   [list with %]     │
├─────────────────────────────────────────────┤
│ Upcoming Bills (next 7 days)               │
│  Netflix  KES 1,200  Due Jun 28  [Pay]     │
│  Rent     KES 25,000 Due Jul 1   [Pay]     │
├─────────────────────────────────────────────┤
│ Savings Goals Snapshot                     │
│  Emergency Fund  45%  ██████░░░░  [View]   │
│  Vacation        70%  ███████░░░  [View]   │
├─────────────────────────────────────────────┤
│ vs Last Month: Income ↑12%  Expenses ↓3%   │
└─────────────────────────────────────────────┘
```

---

## 8. Tech Stack & Architecture

### 8.1 Technology Choices

| Layer | Technology |
|---|---|
| **Backend framework** | Django 6.0.6, Django REST Framework 3.17.1 |
| **Auth** | djangorestframework-simplejwt (rotation + blacklisting) |
| **Database** | PostgreSQL 16 (Docker Compose) |
| **Frontend** | React 19.2.6, TypeScript 6.0.2, Vite 8.0.12, react-router-dom 7.17.0 |
| **API documentation** | drf-spectacular (Swagger UI + OpenAPI schema) |
| **Rate limiting** | django-ratelimit |
| **CORS** | django-cors-headers |
| **Containerization** | Docker Compose (PostgreSQL only) |
| **Deployment** | Railway (Django) + Vercel (React) |
| **Styling** | Custom CSS (dark theme, no framework) |

### 8.2 Project Structure

```
ching-track/
├── backend/
│   ├── config/settings/         # base.py, development.py, production.py
│   ├── apps/
│   │   ├── accounts/            # CustomUser, auth views, email verification, GDPR
│   │   ├── transactions/        # Category + Transaction models, views, M-Pesa parser
│   │   ├── budgets/             # Budget + UserPreferences models, views
│   │   ├── bills/               # Bill + BillPayment models, views
│   │   ├── goals/               # SavingsGoal + GoalContribution models, views
│   │   └── analytics/           # Dashboard + trends aggregation views
│   ├── core/                    # IsOwner permission, pagination, exception handler, CSP
│   ├── seed.py                  # Comprehensive test data seeder
│   └── manage.py
├── frontend/react/
│   └── src/
│       ├── api/                 # 10 service modules + centralized client.ts
│       ├── components/          # Layout, ProtectedRoute, Icons
│       ├── context/             # AuthContext
│       ├── pages/               # 15 page components
│       ├── types/               # 8 TypeScript interface files
│       └── utils/               # format.ts
├── docs/                        # PRD.md, WEEK1_IMPLEMENTATION_PLAN.md
├── docker-compose.yml           # PostgreSQL 16
└── pyproject.toml               # Root Python project definition
```

### 8.3 Key Architectural Decisions

- **API-first**: Django serves pure REST API; React SPA is fully separate
- **User-scoped data**: Every query filters by `user=request.user` + `IsOwner` permission
- **Computed fields**: Budget spend, goal progress, bill due dates computed at query time (never stored)
- **Soft deletes**: Transactions (`is_deleted`) + bills (`is_active`) for audit trail
- **Decimal for money**: All monetary values use `DecimalField` — never floats
- **No global state library**: Each page self-contained; `AuthContext` only for auth
- **JWT in localStorage**: Simple token storage with auto-refresh logic
- **Signals for defaults**: `UserPreferences` + 16 default `Category` entries created on registration
- **CSP in production**: Content Security Policy headers via middleware

---

## 9. Security

| Feature | Implementation |
|---|---|
| **Authentication** | JWT access (60min) + refresh (7d) with rotation and blacklisting |
| **Authorization** | `IsOwner` permission class on all detail views |
| **Rate limiting** | 3–10 requests/min/IP on all public auth endpoints |
| **CSP** | Content Security Policy headers in production |
| **HSTS** | Strict-Transport-Security in production |
| **SSL** | Secure cookies + SSL redirect in production |
| **Error handling** | Custom exception handler — no stack trace leakage, consistent JSON format |
| **Money** | `DecimalField` for all monetary values — no floating-point errors |
| **Validation** | Input validation on all fields (amount > 0, category required, etc.) |
| **Enumeration prevention** | Password reset returns same response whether email exists or not |
| **XSS prevention** | `html.escape` on M-Pesa parser output |

---

## 10. Seed Data

`python backend/manage.py shell -c "import seed; seed.run()"` creates:

| Entity | Count | Details |
|---|---|---|
| User | 1 | `test@chingtrack.com` / `Test1234!` |
| Preferences | 1 | KES, 80,000 monthly limit |
| Categories | 19 | 16 defaults + 3 custom |
| Transactions | ~45 | 3 months of data with edge cases |
| Budgets | 9 | Safe/warning/over scenarios |
| Bills | 12 | Monthly/weekly/once, some paid, overdue, upcoming |
| Goals | 7 | Completed, on-track, behind, no-deadline, zero-contributions |

---

## 11. Deployment

### Backend (Railway)
- `DJANGO_SETTINGS_MODULE=config.settings.production`
- Gunicorn WSGI server
- Environment variables: `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `FRONTEND_URL`, email config

### Frontend (Vercel)
- `pnpm build` → `dist/` output
- Dev proxy: `/api` → `localhost:8000`

### Docker
- PostgreSQL 16 via `docker-compose.yml`

---

## 12. Testing

Currently limited to M-Pesa parser unit tests (182 lines, 29 test cases at `backend/apps/transactions/tests/test_mpesa_parser.py`):

- `_extract_amount` — 9 cases (KES with commas, decimals, edge cases)
- `_extract_ref` — 3 cases (standard, alphanumeric, absent)
- `_extract_counterparty` — 7 cases (names, XSS sanitization)
- `_classify` — 5 cases (send, receive, paybill, buy goods, airtime)
- `parse_mpesa_sms` — 8 cases (full pipeline with valid/invalid/XSS input)

---

## 13. Future Roadmap

### 13.1 AI Financial Advisor
- Conversational assistant using user's transaction data
- Claude/Gemini via tool-calling pattern
- Requires: LLM API cost, prompt engineering, chat UI

### 13.2 Financial Habit Tracking
- Behavioral pattern detection (streaks, day-of-week trends, engagement)
- Requires: Celery + Redis for background computation, 60+ days of user data

### 13.3 Financial Goal Prediction Engine
- ML model predicting goal achievement probability
- Upgrade path: linear extrapolation → regression → Monte Carlo simulation
- Current `is_on_track` field is the seed of this feature

### 13.4 M-Pesa Daraja API Integration
- Real-time webhook from Safaricom
- Requires: registered business/paybill account

### 13.5 Other Deferred Features

| Feature | Notes |
|---|---|
| Shared budgets (couples/roommates) | Multi-user auth, invite system, permission model |
| Mobile app | JWT ready; needs push notifications |
| PDF / CSV export | Add after GDPR export is proven |
| Investment tracking | New `Portfolio` + `AssetHolding` models |
| Tax reporting (KRA) | Requires Kenya tax bracket logic |
| Offline-first PWA | IndexedDB + sync protocol |
| Recurring transaction auto-creation | Celery beat task |
| Notifications / reminders | Email or in-app bill/goal reminders |

