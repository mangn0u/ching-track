# Product Requirements Document
## Personal Finance Tracker — 2-Week MVP

**Version:** 1.0  
**Owner:** Mang'nu
**Timeline:** 2 weeks (≈60 hours @ 4hrs/day, 15 days)  **Stack:** React + Tailwind CSS (frontend) · Django + PostgreSQL (backend)  
**Deployment Target:** Localhost (Week 1) → Railway (Django) + Vercel (React + Tailwind) (Week 2, Day 13)

---

## 1. Problem Statement

### Why Does This Exist?

We live in a world where most of us operate without a system for tracking income, spending, and savings goals consistently make decisions in an information vacuum. The result is lifestyle inflation, surprise bills, and savings that never compound. The problem is not willpower — it is architecture. You need a single source of truth that shows you where money is going in real time.

### What Problem Does It Solve?

| Symptom | Root Cause | This Tool Fixes |
|---|---|---|
| "I don't know where my money went" | No transaction log | Transaction entry + category drill-down |
| "I forgot that bill was due" | No bill calendar | Bill tracker with due dates |
| "I never hit my savings targets" | No visible goal progress | Savings goals with progress bars |
| "My budget is just a spreadsheet guess" | No feedback loop | Budget vs actuals per category |

### Constraints That Shape This Solution

- **Solo builder, 4hrs/day** → No microservices. One Django app, one React SPA.
- **No external APIs in MVP** → No bank connections. Manual entry only. M-Pesa SMS parsing is v2.
- **Multi-currency** → Store `currency_code` per transaction from Day 1. No conversion in MVP.
- **Target scale** → 1,000 users. User data fully isolated (row-level scoping on every query).

---

## 2. MVP Scope (The Hard Line)

> **Rule:** If it doesn't make the core loop — *log a transaction → see where you stand → adjust* — it is out.

### ✅ In Scope

1. **Authentication** — register (email verification), login, logout, password reset (JWT via SimpleJWT)
2. **Transaction Management** — create, read, update, delete income + expense transactions
3. **Category System** — predefined categories + user can add custom ones
4. **Budget Planner** — set a monthly spend limit per category; see actual vs budget
5. **Savings Goals** — create a goal with a target amount + deadline; log contributions; on-track indicator
6. **Global Spending Limit** — set a single monthly spend ceiling (e.g. KES 80,000); see how much remains
7. **User Preferences** — preferred currency, monthly spending limit, profile settings
8. **Bill Tracker** — log recurring bills with due dates; mark as paid
9. **Dashboard** — monthly summary: income, expenses, net, savings rate, category breakdown, month-over-month
10. **Data Privacy** — GDPR-style: full data export (JSON) + account deletion

### ❌ Out of Scope (Not in 2 Weeks)

- Bank sync / Plaid integration
- Multi-user / sharing
- Mobile app
- PDF/CSV export
- Notifications / reminders
- AI categorization
- Investment tracking
- Tax reports

---

## 3. User Stories (Prioritized)

**Priority: Must Have (Week 1 backend + Week 2 frontend)**

| ID | Story | Acceptance Criteria |
|---|---|---|
| U1 | As a user, I can log in and have my data be private | Login with email + password; unauthenticated requests return 401 |
| U2 | As a user, I can add a transaction with amount, category, date, note | Form validates: amount > 0, category required, date required |
| U3 | As a user, I can see all transactions in a list, filterable by month | Default view = current month; filter by prev months |
| U4 | As a user, I can edit or delete any transaction | Changes reflect immediately in dashboard totals |
| U5 | As a user, I can see my spending breakdown by category this month | Dashboard bar chart: category vs amount spent |
| U6 | As a user, I can set a monthly budget for each category | Input per category; shown as limit in dashboard |
| U7 | As a user, I can add a bill with name, amount, due date, recurrence | Fields: name, amount, due_day (1-31), frequency (monthly/weekly) |
| U8 | As a user, I can mark a bill as paid for the current period | Paid status resets next cycle |
| U9 | As a user, I can create a savings goal with a name, target, deadline | Progress bar = contributions / target |
| U10 | As a user, I can log a contribution to a savings goal | Contribution history shows per goal |

**Priority: Should Have (if time allows)**

| ID | Story |
|---|---|
| U11 | Month-over-month summary: did I spend more or less than last month? |
| U12 | Color-coded category budget indicator (green/yellow/red) |
| U13 | Running balance (income minus expenses, cumulative) |

---

## 4. Data Architecture

> **First Principles Note:** The data model is the contract between your frontend and backend. Get this wrong and you'll be refactoring forever. Every field you add now costs ~5 minutes. Every field you add in Week 3 costs 2 hours.

### 4.1 Entity-Relationship Overview

```
User (Django built-in)
  │
  ├── Category (name, type: income|expense, color, icon, is_default)
  │
  ├── Transaction (amount, type, category_fk, date, note, created_at)
  │
  ├── Budget (category_fk, month, year, limit_amount)
  │
  ├── Bill (name, amount, due_day, frequency, is_active)
  │   └── BillPayment (bill_fk, paid_date, amount_paid)
  │
  └── SavingsGoal (name, target_amount, deadline, created_at)
      └── GoalContribution (goal_fk, amount, date, note)
```

### 4.2 Django Models (Exact Schema)

```python
# transactions/models.py

class Category(models.Model):
    TRANSACTION_TYPES = [('income', 'Income'), ('expense', 'Expense')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    color = models.CharField(max_length=7, default='#6366f1')  # hex
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name', 'type')


class Transaction(models.Model):
    TRANSACTION_TYPES = [('income', 'Income'), ('expense', 'Expense')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.IntegerField()   # 1-12
    year = models.IntegerField()
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')


class Bill(models.Model):
    FREQUENCY_CHOICES = [('monthly', 'Monthly'), ('weekly', 'Weekly'), ('once', 'One-time')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_day = models.IntegerField()  # day of month (1-31)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='monthly')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class BillPayment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    paid_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GoalContribution(models.Model):
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
```

---

## 5. API Design (REST Endpoints)

> **Pattern:** All endpoints are prefixed `/api/v1/`. All require authentication. All return JSON.

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register/` | Create account, send verification email |
| GET | `/api/v1/auth/verify-email/<token>/` | Activate account |
| POST | `/api/v1/auth/login/` | Login → returns `{access, refresh, user}` |
| POST | `/api/v1/auth/token/refresh/` | Rotate JWT tokens |
| POST | `/api/v1/auth/logout/` | Blacklist refresh token |
| GET/PUT | `/api/v1/auth/me/` | View / update profile |
| POST | `/api/v1/auth/forgot-password/` | Send reset email |
| POST | `/api/v1/auth/reset-password/<token>/` | Set new password |
| POST | `/api/v1/auth/change-password/` | Change password (authenticated) |
| GET | `/api/v1/auth/export-data/` | GDPR: export all user data as JSON |
| DELETE | `/api/v1/auth/delete-account/` | GDPR: delete account + all data |

### Transactions

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/transactions/` | List (filter: `?month=6&year=2026&type=expense`) |
| POST | `/api/v1/transactions/` | Create |
| PUT | `/api/v1/transactions/:id/` | Update |
| DELETE | `/api/v1/transactions/:id/` | Delete |
| GET | `/api/v1/transactions/summary/` | Monthly totals: `{income, expense, net, by_category[]}` |

### Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/categories/` | List all user's categories |
| POST | `/api/v1/categories/` | Create custom category |
| DELETE | `/api/v1/categories/:id/` | Delete (only if no transactions linked) |

### Budgets

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/budgets/` | List (`?month=6&year=2026`) |
| POST | `/api/v1/budgets/` | Set/update budget for category+month |
| GET | `/api/v1/budgets/vs-actual/` | Budget limit vs actual spend per category |

### Bills

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/bills/` | List active bills |
| POST | `/api/v1/bills/` | Create bill |
| PUT | `/api/v1/bills/:id/` | Edit |
| DELETE | `/api/v1/bills/:id/` | Soft delete (set `is_active=False`) |
| POST | `/api/v1/bills/:id/pay/` | Mark paid → creates BillPayment record |

### Savings Goals

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/goals/` | List goals with `total_saved`, `progress_pct` |
| POST | `/api/v1/goals/` | Create goal |
| PUT | `/api/v1/goals/:id/` | Edit |
| POST | `/api/v1/goals/:id/contribute/` | Add contribution |
| GET | `/api/v1/goals/:id/contributions/` | Contribution history |

---

## 6. Frontend Architecture

### Pages & Routes

```
/login             → LoginPage
/register          → RegisterPage
/                  → Dashboard (protected)
/transactions      → TransactionListPage (protected)
/transactions/new  → TransactionFormPage
/budgets           → BudgetPage
/bills             → BillsPage
/goals             → GoalsPage
```

### Component Map

```
App
├── AuthProvider (Context: user, login, logout)
├── Layout
│   ├── Sidebar (nav links)
│   └── <Outlet /> (react-router)
├── Dashboard
│   ├── SummaryCards (Income | Expenses | Net | Savings)
│   ├── CategoryBreakdownChart (horizontal bar)
│   ├── BudgetStatusList (limit vs actual, color coded)
│   └── UpcomingBills (next 7 days)
├── TransactionListPage
│   ├── MonthSelector
│   ├── TransactionFilters (type, category)
│   └── TransactionTable (with edit/delete)
├── BudgetPage
│   └── BudgetCategoryRow (per category: input + actuals)
├── BillsPage
│   ├── BillCard (name, amount, due date, pay button)
│   └── AddBillForm
└── GoalsPage
    ├── GoalCard (name, progress bar, contribute button)
    └── AddGoalForm
```

### State Management Strategy

> **No Redux. No Zustand.** You don't need global state for an MVP with one user.

- **Auth state:** React Context (`AuthContext`)
- **Server data:** Fetch directly in each page component with `useEffect`. Store in local `useState`.
- **Forms:** Controlled components with local `useState`.
- **Error handling:** Local state per form/component.

---

## 7. UI/UX Guidelines

### Design System

- **Theme:** Dark editorial (consistent with your Spark Lite aesthetic)
- **Primary font:** System font stack or `IBM Plex Mono` for numbers
- **Color palette:**
  - Background: `#0f0f0f`
  - Surface: `#1a1a1a`
  - Border: `#2a2a2a`
  - Accent: `#22d3ee` (cyan — income)
  - Danger: `#f43f5e` (rose — expense)
  - Muted: `#6b7280`
- **Key principle:** Numbers always right-aligned. Income always cyan. Expense always rose.

### Dashboard Layout (wireframe logic)

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
└─────────────────────────────────────────────┘
```

---

## 8. Week-by-Week Build Plan

> **Rule:** Every day ends with something that runs. No "setup days". No dead ends.

### WEEK 1 — Backend & Foundation (30 hours)

**Goal: A working REST API you can test in Postman/curl. No frontend yet.**

| Day | Hours | Deliverable | Done When |
|---|---|---|---|
| **Day 1** | 4h | Django project setup, models, migrations | `python manage.py migrate` runs clean. All 6 models exist in DB |
| **Day 2** | 4h | Auth endpoints (register, login, logout, me) | Can register + login via curl. Session cookie works |
| **Day 3** | 4h | Transaction CRUD endpoints + category endpoints | CRUD tested in Postman. Filter by month/year works |
| **Day 4** | 4h | Budget endpoints + `vs-actual` computed endpoint | `GET /budgets/vs-actual/` returns `{category, limit, actual, remaining}[]` |
| **Day 5** | 4h | Bills endpoints (CRUD + `/pay/`) | Can create bill, mark paid, payment logged |
| **Day 6** | 4h | Savings Goals endpoints + contribution logic | Goal shows `total_saved` and `progress_pct` computed |
| **Day 7** | 2h | Seed data script + basic error handling review | `python seed.py` populates 3 months of fake data |

**Week 1 Architecture Decisions:**

- Use `django-cors-headers` from Day 1 (you'll need it for frontend)
- Use `djangorestframework` for serializers + class-based views
- All money stored as `DecimalField` — never `FloatField` (floating point errors in finance = bugs)
- All dates stored as `DateField`, not `DateTimeField` (timezone bugs kill MVPs)
- User scoping: every queryset filters `user=request.user` — **test this explicitly**

---

### WEEK 2 — Frontend & Integration (30 hours)

**Goal: A working React SPA connected to your live API. Deployed by Day 14.**

| Day | Hours | Deliverable | Done When |
|---|---|---|---|
| **Day 8** | 4h | React + Tailwind + React Router setup. Auth flow (login/register pages). `AuthContext` | Can log in, session persists on refresh |
| **Day 9** | 4h | Dashboard page: summary cards + category bar chart | Numbers match what API returns. Chart renders |
| **Day 10** | 4h | Transaction list page: table + month filter + add/edit/delete | Full CRUD works end-to-end |
| **Day 11** | 4h | Budget page: set limits, see vs-actual with color coding | Red/yellow/green status per category updates on save |
| **Day 12** | 4h | Bills page + Goals page | Pay button works. Contribution modal works. Progress bar updates |
| **Day 13** | 4h | Deploy backend (Railway) + frontend (Vercel/Netlify). Fix CORS/env vars | App is live at a URL you can share |
| **Day 14** | 2h | Bug fixes, polish, write a README | README explains what it does + how to run locally |

**Week 2 Architecture Decisions:**

- Use `fetch` with `credentials: 'include'` for session cookie auth (simpler than JWT for an MVP)
- Create one `api.js` utility file that wraps all fetch calls (easier to swap base URL for prod)
- Use `recharts` for charts (already in your React toolkit from Spark Lite context)
- Mobile responsive but desktop-first (80% of budget work happens on desktop)

---

## 9. Technical Constraints & Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| CORS issues between React dev server and Django | High | Medium | Install `django-cors-headers` on Day 1, configure before writing any frontend |
| Session auth breaks in prod (Vercel + Railway = cross-domain) | High | High | Switch to JWT (`djangorestframework-simplejwt`) on Day 13 if needed. localStorage for token |
| Data model changes after Week 1 | Medium | High | Finalize schema before writing any serializers. Schema changes after Day 3 = costly |
| Scope creep on Day 9-12 | High | High | If a feature isn't in this PRD, add it to a `v2-backlog.md` file. Do not touch it |
| Chart library complexity | Low | Low | `recharts` is beginner-friendly. Use `BarChart` only — no custom renderers |

---

## 10. Definition of Done (MVP Complete)

The MVP is done when a user can:

- [ ] Register and log in with email + password
- [ ] Add, edit, delete a transaction (income or expense)
- [ ] See this month's total income, expenses, and net balance on a dashboard
- [ ] See a bar chart of spending by category
- [ ] Set a monthly budget limit for any category and see how much is remaining
- [ ] Add a recurring bill and mark it as paid
- [ ] Create a savings goal and log a contribution
- [ ] See goal progress as a percentage bar

All of the above must work on the **deployed URL**, not just localhost.

---

## 11. Business Layer — Why This Matters Beyond the Build

### What You're Actually Building

A finance tracker is a **data capture + insight loop**. The value isn't the CRUD — it's the behavior change it creates. Users who see their spending lose the ability to rationalize it.

### Portfolio Framing

When presenting this to a client or in a job application:

> "Built a personal finance system with a Django REST API and React frontend. Designed a normalized data schema tracking transactions, budgets, bills, and savings goals across multiple time periods. Implemented computed endpoints for budget-vs-actual analysis, deployed on Railway + Vercel."

That signals: **API design thinking, data modeling, deployment experience** — which is exactly what a data engineering-adjacent full-stack role wants.

### Productization Path (Post-MVP)

If you wanted to sell this as a service:

- **SaaS:** KES 499/month per user. Target: salaried professionals, freelancers
- **Differentiator:** Offline-first (PWA), Kenya-native (M-Pesa import)
- **Distribution:** Twitter/X for Kenyan professionals, LinkedIn for fintech positioning

### v2 Backlog (Don't Touch in 2 Weeks)

- M-Pesa SMS parser → auto-import transactions
- CSV export
- Recurring transaction auto-creation
- Shared budgets (couples/roommates)
- AI categorization (send transaction note → Claude API → returns category)

---

## 12. Daily Routine (Time Budget)

```
Hour 1: Review yesterday's output. Fix any broken tests or endpoints.
Hour 2-3: Build the day's deliverable (backend or frontend).
Hour 4: Test manually. Commit. Write one sentence in your dev log.
```

---

## 13. Future Features (Post-MVP Roadmap)

> These are explicitly **out of scope** for the 2-week MVP. They are documented here to ensure the current architecture does not block their future implementation.

### 13.1 AI Financial Advisor

**What:** A conversational assistant that answers questions about the user's finances using their actual transaction data.

**Example interactions:**
- *"Why did I overspend in March?"* → AI analyses category breakdown
- *"How much can I safely spend this weekend?"* → AI checks remaining budget + upcoming bills
- *"Am I on track to hit my savings goal?"* → AI factors in current pace + deadline

**Architecture notes (design for this now):**
- Keep transaction data structured and queryable — the AI needs clean aggregates, not raw text
- A `financial_summary` computed view/endpoint will feed context to the LLM
- Use tool-calling (function calling) pattern: LLM calls internal API functions, not raw SQL
- Model: Claude or Gemini via API. Wrap in a Django view that assembles context + calls LLM.

**Why not MVP:** Requires LLM API cost, prompt engineering, and a chat UI. Not core to the "log + see" loop.

---

### 13.2 Financial Habit Tracking System

**What:** Tracks behavioral patterns over time — not just numbers, but *how* the user manages money.

**Examples:**
- "You've logged transactions every day for 14 days" (streak)
- "You tend to overspend on Fridays" (day-of-week pattern)
- "Your Food spending increases by 30% in the last week of the month" (pattern detection)
- "You set budgets but rarely check them mid-month" (engagement insight)

**Architecture notes:**
- Add a `UserHabit` model: `{user, habit_type, streak_count, last_triggered, metadata_json}`
- Habits are computed by a background task (Celery + Redis) running nightly
- Store habit snapshots — don't recompute on every request
- The AI Advisor (13.1) will use habit data as additional context

**Why not MVP:** Requires background task infrastructure (Celery + Redis) and enough historical data (need 60+ days of user behaviour) to be meaningful.

---

### 13.3 Financial Goal Prediction Engine

**What:** Uses historical contribution pace + spending patterns to predict whether the user will achieve their savings goals by the deadline — and by how much they're off.

**Examples:**
- "At your current savings rate, you'll reach your Emergency Fund goal 3 months late"
- "If you cut Entertainment spending by 20%, you'll hit your goal on time"
- "There is an 82% probability you'll achieve this goal" (probabilistic model)

**Architecture notes:**
- Start simple: linear extrapolation from current `total_saved` + `days_remaining`
- Upgrade to: regression model trained on user's own contribution history
- Final form: Monte Carlo simulation using spending variance + income variance
- Expose as a computed field `prediction` on the `SavingsGoal` endpoint — the data model is already set
- The `is_on_track` boolean on MVP SavingsGoal is the seed of this feature

**Why not MVP:** Requires sufficient historical data and a separate ML/stats service. `is_on_track` in the MVP is the v1 of this feature.

---

### 13.4 M-Pesa Integration (Daraja API / SMS Parsing)

**What:** Automatically import M-Pesa transactions instead of manual entry.

**Two approaches:**
- **SMS Parsing (v2):** User pastes or forwards M-Pesa SMS → regex extracts `{amount, ref, type, counterparty}` → auto-creates Transaction. No business account needed.
- **Daraja API (v3):** Real-time webhook from Safaricom. Requires registered business/paybill. For when this becomes a SaaS product.

**Architecture notes (already prepared in MVP):**
- `Transaction.mpesa_ref` and `Transaction.mpesa_raw_sms` fields added in Week 1
- `CustomUser.mpesa_phone` field added in Week 1
- A future `POST /api/v1/mpesa/parse-sms/` endpoint will accept raw SMS text and return a pre-filled Transaction object for user confirmation before saving

**Why not MVP:** Parsing accuracy requires testing across all M-Pesa SMS formats (send, receive, buy goods, pay bill, withdraw). Not suitable for a 2-week build.

---

### 13.5 Other Deferred Features

| Feature | Notes |
|---|---|
| Shared budgets (couples/roommates) | Needs multi-user auth, invite system, permission model |
| Mobile app (React Native / Flutter) | JWT auth is already mobile-ready. Add push notifications. |
| PDF / CSV export | Add after data export (GDPR endpoint) is proven |
| Investment tracking | New asset class. Separate `Portfolio` + `AssetHolding` models. |
| Tax reporting (KRA) | Requires understanding of Kenya tax brackets. Post-product-market fit. |
| Multi-device offline sync | PWA + IndexedDB + sync protocol. Major complexity. |
| Recurring transaction auto-creation | Celery beat task. Simple to add once background tasks exist. |

