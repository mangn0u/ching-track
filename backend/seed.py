"""
Database seeding script.
Populates the database with a test user and 3 months of realistic financial data.
Can be executed via: python backend/manage.py shell -c "import seed; seed.run()"
"""

import os
import random
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.accounts.models import CustomUser
from apps.budgets.models import UserPreferences, Budget
from apps.transactions.models import Transaction, Category
from apps.bills.models import Bill, BillPayment
from apps.goals.models import SavingsGoal, GoalContribution

User = get_user_model()


def run():
    print("🚀 Starting Database Seed Script...")

    # We use a database transaction block to ensure atomic operations
    with transaction.atomic():
        email = "test@chingtrack.com"
        password = "Test1234!"

        # 1. Clean up existing test user
        print(f"🧹 Cleaning up existing test user: {email}...")
        User.objects.filter(email=email).delete()

        # 2. Create the primary Test User
        print(f"👤 Creating test user: {email}...")
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name="Mang'nu",
            last_name="Developer",
            phone_number="+254712345678",
            mpesa_phone="+254712345678",
            is_email_verified=True,
        )

        # Retrieve categories seeded automatically by signals
        categories = Category.objects.filter(user=user)
        category_map = {cat.name: cat for cat in categories}
        print(f"🌱 Signal seeded {len(category_map)} default categories automatically.")

        # 3. Configure User Preferences
        print("⚙️ Updating User Preferences...")
        prefs = UserPreferences.objects.get(user=user)
        prefs.currency = "KES"
        prefs.monthly_spending_limit = 80000.00
        prefs.save()

        # 4. Generate 90 Days of Realistic Transactions
        print("💸 Generating 3 months (90 days) of transactions...")
        today = date.today()
        start_date = today - timedelta(days=90)

        # Let's seed consistent monthly income first
        current_date = start_date
        while current_date <= today:
            day = current_date.day
            month = current_date.month
            year = current_date.year

            # Monthly Salary on 1st
            if day == 1:
                Transaction.objects.create(
                    user=user,
                    category=category_map["Salary"],
                    type="income",
                    amount=120000.00,
                    currency_code="KES",
                    date=current_date,
                    note="Monthly Salary Payment",
                )
                print(f"   [Income] Seeded Salary for {current_date.strftime('%B %Y')}")

            # Mid-month Freelance on 15th (in USD to show multi-currency support)
            if day == 15:
                Transaction.objects.create(
                    user=user,
                    category=category_map["Freelance"],
                    type="income",
                    amount=250.00,
                    currency_code="USD",
                    date=current_date,
                    note="Website freelance design retainer",
                )
                print(f"   [Income] Seeded Freelance retainer (USD) for {current_date.strftime('%B %Y')}")

            # Recurring rent on 2nd
            if day == 2:
                Transaction.objects.create(
                    user=user,
                    category=category_map["Housing"],
                    type="expense",
                    amount=25000.00,
                    currency_code="KES",
                    date=current_date,
                    note="Apartment Rent Payment",
                )

            # Random daily expenses based on category
            # Food spending
            if random.random() < 0.25:  # ~once every 4 days
                amount = round(random.uniform(300.0, 2500.0), 2)
                Transaction.objects.create(
                    user=user,
                    category=category_map["Food"],
                    type="expense",
                    amount=amount,
                    currency_code="KES",
                    date=current_date,
                    note=random.choice([
                        "Supermarket Groceries", "Choma lunch with friend", 
                        "Coffee and snacks", "KFC Friday deal"
                    ]),
                )

            # Transport spending
            if random.random() < 0.20:
                amount = round(random.uniform(150.0, 1000.0), 2)
                Transaction.objects.create(
                    user=user,
                    category=category_map["Transport"],
                    type="expense",
                    amount=amount,
                    currency_code="KES",
                    date=current_date,
                    note=random.choice(["Uber ride", "Fuel", "Matatu fare"]),
                )

            # Entertainment spending
            if random.random() < 0.10:
                amount = round(random.uniform(500.0, 5000.0), 2)
                Transaction.objects.create(
                    user=user,
                    category=category_map["Entertainment"],
                    type="expense",
                    amount=amount,
                    currency_code="KES",
                    date=current_date,
                    note=random.choice(["Movie ticket & popcorn", "Weekend hangout", "Video game purchase"]),
                )

            # Shopping spending
            if random.random() < 0.08:
                amount = round(random.uniform(1000.0, 8000.0), 2)
                Transaction.objects.create(
                    user=user,
                    category=category_map["Shopping"],
                    type="expense",
                    amount=amount,
                    currency_code="KES",
                    date=current_date,
                    note=random.choice(["New clothes", "Electronics accessory", "Home decor"]),
                )

            # Small M-Pesa Sent
            if random.random() < 0.15:
                amount = round(random.uniform(200.0, 3000.0), 2)
                Transaction.objects.create(
                    user=user,
                    category=category_map["M-Pesa Sent"],
                    type="expense",
                    amount=amount,
                    currency_code="KES",
                    date=current_date,
                    note="Sent to vendor via M-Pesa",
                    mpesa_ref=f"RK{random.randint(100000, 999999)}Z{random.randint(10, 99)}",
                )

            current_date += timedelta(days=1)

        # 5. Seed Budgets for current month and previous month
        print("📊 Seeding monthly category budgets...")
        months_to_budget = [
            (today.month, today.year),
            ((today - timedelta(days=28)).month, (today - timedelta(days=28)).year),
        ]

        for m, y in months_to_budget:
            Budget.objects.create(
                user=user,
                category=category_map["Food"],
                month=m,
                year=y,
                limit_amount=15000.00,
            )
            Budget.objects.create(
                user=user,
                category=category_map["Transport"],
                month=m,
                year=y,
                limit_amount=5000.00,
            )
            Budget.objects.create(
                user=user,
                category=category_map["Utilities"],
                month=m,
                year=y,
                limit_amount=8000.00,
            )
            Budget.objects.create(
                user=user,
                category=category_map["Entertainment"],
                month=m,
                year=y,
                limit_amount=10000.00,
            )

        # 6. Seed Bills
        print("📅 Seeding recurring bills...")
        # Bill 1: Netflix
        netflix_bill = Bill.objects.create(
            user=user,
            name="Netflix Subscription",
            amount=1200.00,
            due_day=28,
            frequency="monthly",
            is_active=True,
        )
        # Record payment for previous month
        prev_month_date = today - timedelta(days=28)
        BillPayment.objects.create(
            bill=netflix_bill,
            paid_date=date(prev_month_date.year, prev_month_date.month, 28),
            amount_paid=1200.00,
            note="Previous month auto-payment",
        )

        # Bill 2: Rent Bill (helps trigger upcoming warnings)
        rent_bill = Bill.objects.create(
            user=user,
            name="Apartment Rent",
            amount=25000.00,
            due_day=2,
            frequency="monthly",
            is_active=True,
        )
        # Payment for previous month
        BillPayment.objects.create(
            bill=rent_bill,
            paid_date=date(prev_month_date.year, prev_month_date.month, 2),
            amount_paid=25000.00,
            note="Previous month rent",
        )

        # Bill 3: Internet (due in next 5 days, unpaid)
        due_day_target = (today + timedelta(days=3)).day
        internet_bill = Bill.objects.create(
            user=user,
            name="Safaricom Home Fibre",
            amount=3000.00,
            due_day=due_day_target,
            frequency="monthly",
            is_active=True,
        )

        # 7. Seed Savings Goal & Contributions
        print("🎯 Seeding savings goals and milestones...")
        goal = SavingsGoal.objects.create(
            user=user,
            name="Emergency Fund",
            description="6 months of essential living expenses saved.",
            target_amount=100000.00,
            currency_code="KES",
            deadline=today + timedelta(days=180),
        )

        # Goal Contributions
        contribution_dates = [
            today - timedelta(days=75),
            today - timedelta(days=45),
            today - timedelta(days=15),
        ]
        for idx, c_date in enumerate(contribution_dates):
            amount = 10000.00 if idx != 1 else 15000.00
            GoalContribution.objects.create(
                goal=goal,
                amount=amount,
                date=c_date,
                note=f"Contribution milestone {idx + 1}",
            )

    print("\n🎉 Seeding Completed Successfully!")
    print("---------------------------------------------")
    print(f"Username / Email: {email}")
    print(f"Password:         {password}")
    print("---------------------------------------------")
    print("Enjoy testing ching-track REST APIs! 🚀\n")
