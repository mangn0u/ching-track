"""
Seed script for ChingTrack — run with:
  python3 backend/manage.py shell -c "import seed; seed.run()"

Creates (or reuses) a test user and populates every page:
  - Categories (default already seeded by signal)
  - Transactions  → edge cases: no category, zero-note, M-Pesa ref, soft-deleted
  - Budgets       → safe / warning / over-limit + zero-spend category
  - Bills         → monthly / weekly / one-time, paid / unpaid, overdue
  - Goals         → completed, on-track, behind, no-deadline, zero-contribution
  - Preferences   → currency + monthly spending limit

All data is scoped to the test user (idempotent — safe to run multiple times).
"""

import os, sys, django
from decimal import Decimal
from datetime import date, timedelta

# ── Allow running directly (outside shell -c) ──────────────────────────────────
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()

# ── Imports (after django.setup) ───────────────────────────────────────────────
from apps.accounts.models import CustomUser
from apps.transactions.models import Category, Transaction
from apps.budgets.models import Budget, UserPreferences
from apps.bills.models import Bill, BillPayment
from apps.goals.models import SavingsGoal, GoalContribution


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

TODAY = date.today()
THIS_MONTH = TODAY.month
THIS_YEAR  = TODAY.year

def months_ago(n):
    """Return the first day of the month n months before today."""
    m = TODAY.month - n
    y = TODAY.year
    while m <= 0:
        m += 12
        y -= 1
    return date(y, m, 1)

def day_this_month(day):
    """Return date(THIS_YEAR, THIS_MONTH, day), clamped to last day of month."""
    import calendar
    last = calendar.monthrange(THIS_YEAR, THIS_MONTH)[1]
    return date(THIS_YEAR, THIS_MONTH, min(day, last))


# ──────────────────────────────────────────────────────────────────────────────
# 1. User
# ──────────────────────────────────────────────────────────────────────────────

def get_or_create_user():
    email = "test@chingtrack.com"
    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={
            "first_name": "Test",
            "last_name": "User",
            "is_email_verified": True,
            "is_active": True,
        },
    )
    if created:
        user.set_password("Test1234!")
        user.save()
        print(f"  ✔ Created user: {email}")
    else:
        # Make sure email is verified so login works
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save()
        print(f"  ℹ  User already exists: {email}")
    return user


# ──────────────────────────────────────────────────────────────────────────────
# 2. Preferences
# ──────────────────────────────────────────────────────────────────────────────

def seed_preferences(user):
    prefs, _ = UserPreferences.objects.get_or_create(user=user)
    prefs.currency = "KES"
    prefs.monthly_spending_limit = Decimal("80000.00")
    prefs.save()
    print("  ✔ Preferences set  (KES, limit 80,000)")


# ──────────────────────────────────────────────────────────────────────────────
# 3. Categories  (signal already seeds defaults — we just fetch them)
# ──────────────────────────────────────────────────────────────────────────────

def get_categories(user):
    cats = {c.name: c for c in Category.objects.filter(user=user)}
    print(f"  ✔ Found {len(cats)} categories")
    return cats


def add_custom_categories(user, cats):
    """Add a few custom categories to test the Categories page."""
    customs = [
        {"name": "Side Hustle",  "type": "income",  "color": "#f59e0b", "icon": "🔧"},
        {"name": "Subscriptions","type": "expense", "color": "#6366f1", "icon": "📺"},
        {"name": "Savings Transfer", "type": "expense", "color": "#0ea5e9", "icon": "🏦"},
    ]
    for c in customs:
        obj, created = Category.objects.get_or_create(
            user=user, name=c["name"], type=c["type"],
            defaults={"color": c["color"], "icon": c["icon"], "is_default": False},
        )
        cats[obj.name] = obj
        if created:
            print(f"  ✔ Custom category: {obj.name}")
    return cats


# ──────────────────────────────────────────────────────────────────────────────
# 4. Transactions
# ──────────────────────────────────────────────────────────────────────────────

def seed_transactions(user, cats):
    """
    Creates 3 months of transactions covering:
      - Regular income + expenses across categories
      - Transaction with M-Pesa reference
      - Transaction with no note (blank)
      - Transaction with no category (null)
      - Soft-deleted transaction (edge case)
      - Very large amount (stress test decimal field)
      - Very small amount (KES 1)
    """
    Transaction.objects.filter(user=user).delete()  # wipe existing seed data

    def txn(type_, amount, cat_name, date_, note="", mpesa_ref="", mpesa_sms="", deleted=False):
        cat = cats.get(cat_name)
        Transaction.objects.create(
            user=user,
            type=type_,
            amount=Decimal(str(amount)),
            currency_code="KES",
            category=cat,
            date=date_,
            note=note,
            mpesa_ref=mpesa_ref,
            mpesa_raw_sms=mpesa_sms,
            is_deleted=deleted,
        )

    # ── This month ────────────────────────────────────────────────────────────
    txn("income",  120000,  "Salary",        day_this_month(1),  "July salary")
    txn("income",  25000,   "Freelance",     day_this_month(3),  "Logo design gig")
    txn("income",  8000,    "Side Hustle",   day_this_month(5),  "Weekend tutoring")
    txn("income",  2000,    "Gift",          day_this_month(7),  "Birthday gift from aunt")
    txn("income",  500,     "Other Income",  day_this_month(9),  "")   # blank note edge case

    txn("expense", 18500,   "Housing",       day_this_month(1),  "July rent")
    txn("expense", 5200,    "Food",          day_this_month(2),  "Supermarket run")
    txn("expense", 3800,    "Transport",     day_this_month(4),  "Fuel + matatu")
    txn("expense", 1200,    "Utilities",     day_this_month(5),  "KPLC tokens")
    txn("expense", 850,     "Entertainment", day_this_month(6),  "Cinema + popcorn")
    txn("expense", 4200,    "Shopping",      day_this_month(8),  "New shoes")
    txn("expense", 600,     "Subscriptions", day_this_month(9),  "Netflix")
    txn("expense", 300,     "Subscriptions", day_this_month(10), "Spotify")
    txn("expense", 200,     "Education",     day_this_month(11), "Kindle book")
    txn("expense", 10000,   "Savings Transfer", day_this_month(12), "Emergency fund top-up")

    # M-Pesa transaction (with reference + raw SMS)
    txn("expense", 3500, "Food", day_this_month(14),
        note="Zucchini supermarket",
        mpesa_ref="QHX7K3M2NP",
        mpesa_sms="QHX7K3M2NP Confirmed. Ksh3,500.00 sent to ZUCCHINI SUPERMARKET on 14/7/26 at 2:13 PM.")

    # No-category transaction (tests null category rendering)
    txn("expense", 1, None, day_this_month(15), "Parking — minimum charge")  # KES 1

    # Very large amount (stress test)
    txn("income",  1_250_000, "Business", day_this_month(16), "Q2 client payment")

    # Soft-deleted (should NOT appear in list but tests backend filter)
    txn("expense", 9999, "Shopping", day_this_month(13), "Accidentally logged", deleted=True)

    # ── Last month ────────────────────────────────────────────────────────────
    lm = months_ago(1)
    txn("income",  120000, "Salary",      date(lm.year, lm.month, 1),  "June salary")
    txn("income",  15000,  "Freelance",   date(lm.year, lm.month, 10), "Branding project")
    txn("expense", 18500,  "Housing",     date(lm.year, lm.month, 1),  "June rent")
    txn("expense", 6100,   "Food",        date(lm.year, lm.month, 3),  "Weekly groceries x2")
    txn("expense", 4000,   "Transport",   date(lm.year, lm.month, 8),  "Uber rides")
    txn("expense", 12000,  "Health",      date(lm.year, lm.month, 15), "Hospital visit + meds")
    txn("expense", 2500,   "Shopping",    date(lm.year, lm.month, 20), "")  # blank note
    txn("expense", 700,    "Subscriptions",date(lm.year, lm.month, 9), "Netflix + Spotify")
    txn("expense", 3000,   "Entertainment",date(lm.year, lm.month, 22),"Concert tickets")
    txn("expense", 1400,   "Utilities",   date(lm.year, lm.month, 5),  "Water + electricity")

    # ── Two months ago ────────────────────────────────────────────────────────
    tm = months_ago(2)
    txn("income",  120000, "Salary",      date(tm.year, tm.month, 1), "May salary")
    txn("income",  35000,  "Freelance",   date(tm.year, tm.month, 5), "App dev contract")
    txn("expense", 18500,  "Housing",     date(tm.year, tm.month, 1), "May rent")
    txn("expense", 5500,   "Food",        date(tm.year, tm.month, 7), "Groceries")
    txn("expense", 3500,   "Transport",   date(tm.year, tm.month, 12),"Fuel")
    txn("expense", 8000,   "Education",   date(tm.year, tm.month, 3), "Online course")
    txn("expense", 22000,  "Shopping",    date(tm.year, tm.month, 18),"Laptop accessories")  # over budget
    txn("expense", 1200,   "Utilities",   date(tm.year, tm.month, 5), "KPLC")
    txn("expense", 500,    "Entertainment",date(tm.year, tm.month, 25),"Streaming")

    print(f"  ✔ Transactions seeded (3 months + edge cases)")


# ──────────────────────────────────────────────────────────────────────────────
# 5. Budgets  (this month)
# ──────────────────────────────────────────────────────────────────────────────

def seed_budgets(user, cats):
    """
    Edge cases covered:
      - Safe: well under limit
      - Warning: ~80% spent
      - Over: exceeds limit
      - Zero-spend category (budget set but no transactions)
      - Very tight budget (KES 100)
    """
    Budget.objects.filter(user=user, month=THIS_MONTH, year=THIS_YEAR).delete()

    budgets = [
        # (category_name, limit)
        ("Food",           6000),   # warning zone — spent ~5200
        ("Transport",      5000),   # safe — spent ~3800
        ("Housing",        20000),  # safe — spent 18500
        ("Entertainment",  500),    # OVER — spent 850
        ("Shopping",       3000),   # OVER — spent 4200
        ("Health",         2000),   # safe — zero spend this month
        ("Subscriptions",  1000),   # warning — spent 900
        ("Education",      100),    # tight — spent 200, over
        ("Utilities",      1500),   # safe — spent 1200
    ]

    for cat_name, limit in budgets:
        cat = cats.get(cat_name)
        if not cat:
            continue
        Budget.objects.get_or_create(
            user=user, category=cat, month=THIS_MONTH, year=THIS_YEAR,
            defaults={"limit_amount": Decimal(str(limit))},
        )

    print(f"  ✔ Budgets seeded ({len(budgets)} categories — safe/warning/over edge cases)")


# ──────────────────────────────────────────────────────────────────────────────
# 6. Bills
# ──────────────────────────────────────────────────────────────────────────────

def seed_bills(user):
    """
    Edge cases:
      - Monthly bills: some paid, some overdue, some upcoming
      - Weekly bill
      - One-time bill
      - Very small amount (KES 50)
      - Very large amount
    """
    Bill.objects.filter(user=user).delete()

    bills_data = [
        # (name, amount, due_day, frequency, paid_this_month, overdue_months)
        ("Rent",             18500,  1,  "monthly", True,  0),
        ("KPLC Electricity",  1200,  5,  "monthly", True,  0),
        ("Water Bill",         400, 10,  "monthly", False, 0),  # upcoming / not paid
        ("Internet (Safaricom)", 3500, 15, "monthly", False, 0),  # upcoming
        ("Netflix",            600,  9,  "monthly", True,  0),
        ("Spotify",            300, 10,  "monthly", True,  0),
        ("Gym Membership",    2500, 20,  "monthly", False, 0),  # upcoming
        ("Car Insurance",    12000,  1,  "monthly", False, 1),  # overdue — was due last month
        ("Python Course",    5000,   1,  "once",    False, 0),  # one-time, not yet paid
        ("House Cleaning",    800,   1,  "weekly",  False, 0),  # weekly
        ("Parking Fee",        50,  28,  "monthly", False, 0),  # tiny amount
        ("Laptop Loan",      8500,  25,  "monthly", False, 0),  # upcoming
    ]

    for name, amount, due_day, freq, paid, overdue_months in bills_data:
        bill = Bill.objects.create(
            user=user,
            name=name,
            amount=Decimal(str(amount)),
            currency_code="KES",
            due_day=due_day,
            frequency=freq,
            is_active=True,
        )
        if paid:
            BillPayment.objects.create(
                bill=bill,
                paid_date=day_this_month(due_day),
                amount_paid=Decimal(str(amount)),
                note="Paid on time",
            )
        if overdue_months > 0:
            # Mark it as overdue by adding a payment record from a previous month
            # (no payment this month = overdue)
            lm = months_ago(overdue_months + 1)
            BillPayment.objects.create(
                bill=bill,
                paid_date=date(lm.year, lm.month, due_day),
                amount_paid=Decimal(str(amount)),
                note="Last payment",
            )

    print(f"  ✔ Bills seeded ({len(bills_data)} bills — paid/unpaid/overdue/one-time/weekly)")


# ──────────────────────────────────────────────────────────────────────────────
# 7. Savings Goals
# ──────────────────────────────────────────────────────────────────────────────

def seed_goals(user):
    """
    Edge cases:
      - Completed goal (100%+ contributions)
      - On-track goal (ahead of schedule)
      - Behind goal (behind schedule)
      - Goal with no deadline
      - Goal with zero contributions (brand new)
      - Goal with very tight deadline (tomorrow)
      - Goal with very far deadline (5 years)
    """
    SavingsGoal.objects.filter(user=user).delete()

    goals = [
        {
            "name": "Emergency Fund",
            "description": "6 months of expenses saved in a liquid account.",
            "target": 150000,
            "deadline": date(THIS_YEAR, 12, 31),
            "contributions": [
                (months_ago(5), 20000, "Initial deposit"),
                (months_ago(4), 20000, "Month 2"),
                (months_ago(3), 20000, "Month 3"),
                (months_ago(2), 20000, "Month 4"),
                (months_ago(1), 20000, "Month 5"),
                (TODAY,          10000, "Top-up"),
            ],
        },
        {
            "name": "New Laptop",
            "description": "MacBook Pro M4 for development work.",
            "target": 250000,
            "deadline": date(THIS_YEAR + 1, 3, 1),
            "contributions": [
                (months_ago(2), 30000, "First save"),
                (months_ago(1), 30000, "Second save"),
                (TODAY,         30000, "This month"),
            ],
        },
        {
            "name": "Vacation – Zanzibar",
            "description": "Beach holiday, flights + hotel + spending money.",
            "target": 80000,
            "deadline": date(THIS_YEAR, 9, 1),  # tighter deadline — behind schedule
            "contributions": [
                (months_ago(1), 10000, "Started saving"),
                (TODAY,          8000, "Small top-up"),
            ],
        },
        {
            "name": "House Down Payment",
            "description": "Long-term goal — saving for a house in Nairobi.",
            "target": 2_500_000,
            "deadline": date(THIS_YEAR + 5, 1, 1),  # far deadline
            "contributions": [
                (months_ago(5), 50000, "Year start"),
                (months_ago(4), 50000, "Month 2"),
                (months_ago(3), 50000, "Month 3"),
                (months_ago(2), 50000, "Month 4"),
                (months_ago(1), 50000, "Month 5"),
                (TODAY,         50000, "Month 6"),
            ],
        },
        {
            "name": "Wedding Fund",
            "description": "Just started — no contributions yet.",
            "target": 500000,
            "deadline": date(THIS_YEAR + 2, 6, 1),
            "contributions": [],  # edge case: zero contributions
        },
        {
            "name": "Car Repair Fund",
            "description": "Emergency car maintenance savings — no deadline.",
            "target": 40000,
            "deadline": None,  # edge case: no deadline
            "contributions": [
                (months_ago(1), 15000, "Initial"),
                (TODAY,         10000, "Top-up"),
            ],
        },
        {
            "name": "New Headphones",
            "description": "Sony WH-1000XM5 — almost done!",
            "target": 35000,
            "deadline": TODAY + timedelta(days=2),  # tight deadline
            "contributions": [
                (months_ago(2), 12000, "Start"),
                (months_ago(1), 12000, "Midway"),
                (TODAY,         12000, "Final push"),   # slightly over target
            ],
        },
    ]

    for g in goals:
        goal = SavingsGoal.objects.create(
            user=user,
            name=g["name"],
            description=g["description"],
            target_amount=Decimal(str(g["target"])),
            currency_code="KES",
            deadline=g["deadline"],
        )
        for contrib_date, amount, note in g["contributions"]:
            GoalContribution.objects.create(
                goal=goal,
                amount=Decimal(str(amount)),
                date=contrib_date,
                note=note,
            )

    print(f"  ✔ Goals seeded ({len(goals)} goals — completed/on-track/behind/no-deadline/zero-contrib)")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def run():
    print("\n🌱 ChingTrack seed starting...\n")

    print("── User ─────────────────────────────")
    user = get_or_create_user()

    print("\n── Preferences ──────────────────────")
    seed_preferences(user)

    print("\n── Categories ───────────────────────")
    cats = get_categories(user)
    cats = add_custom_categories(user, cats)

    print("\n── Transactions ─────────────────────")
    seed_transactions(user, cats)

    print("\n── Budgets ──────────────────────────")
    seed_budgets(user, cats)

    print("\n── Bills ────────────────────────────")
    seed_bills(user)

    print("\n── Goals ────────────────────────────")
    seed_goals(user)

    print("\n✅ Seed complete!")
    print("   Login: test@chingtrack.com / Test1234!")
    print("   Admin: http://localhost:8000/admin/\n")


if __name__ == "__main__":
    run()
