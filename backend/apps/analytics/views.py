"""Analytics views."""

import calendar
from datetime import date, timedelta
from django.db.models import Sum
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.budgets.models import UserPreferences, Budget
from apps.transactions.models import Transaction
from apps.bills.models import Bill
from apps.goals.models import SavingsGoal
from apps.analytics.serializers import DashboardResponseSerializer


class DashboardView(APIView):
    """
    GET /api/v1/analytics/dashboard/
    Aggregated dashboard view providing a single-request payload containing:
    1. Monthly totals (income, expense, net, savings_rate_pct)
    2. Category-wise expense breakdown with percentages
    3. Category-wise budget limits vs actual expenses
    4. Global spending limit vs actual monthly expenses
    5. Upcoming unpaid bills due in the next 7 days
    6. Savings goals and their progress/track status
    7. Month-over-month percentage changes in income and expenses
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("month", type=int, description="Month (1-12)", required=False),
            OpenApiParameter("year", type=int, description="Year (YYYY)", required=False),
            OpenApiParameter("currency", type=str, description="Currency code (e.g. KES)", required=False),
        ],
        responses={200: DashboardResponseSerializer},
        summary="Fetch user's financial dashboard overview"
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        today = date.today()

        # Parse query parameters with defaults
        month = request.query_params.get("month", today.month)
        year = request.query_params.get("year", today.year)

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response(
                {"error": "Month and Year must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # User Preferences & Currency configuration
        prefs, _ = UserPreferences.objects.get_or_create(user=user)
        currency = request.query_params.get("currency", prefs.currency)

        # ----------------------------------------------------------------------
        # 1 & 2. Transaction aggregates & Spending by Category
        # ----------------------------------------------------------------------
        base_qs = Transaction.objects.filter(
            user=user,
            date__month=month,
            date__year=year,
            currency_code=currency,
            is_deleted=False
        )

        total_income = base_qs.filter(type="income").aggregate(sum=Sum("amount"))["sum"] or 0.0
        total_expense = base_qs.filter(type="expense").aggregate(sum=Sum("amount"))["sum"] or 0.0

        total_income = float(total_income)
        total_expense = float(total_expense)
        net = total_income - total_expense

        savings_rate_pct = 0.0
        if total_income > 0.0 and net > 0.0:
            savings_rate_pct = round((net / total_income) * 100, 2)

        # Category spending breakdown
        category_spending = (
            base_qs.filter(type="expense")
            .values("category__id", "category__name", "category__color", "category__icon")
            .annotate(sum=Sum("amount"))
            .order_by("-sum")
        )

        spending_by_category_data = []
        for cat in category_spending:
            cat_sum = float(cat["sum"])
            pct = round((cat_sum / total_expense) * 100, 2) if total_expense > 0.0 else 0.0
            spending_by_category_data.append({
                "category": cat["category__name"] or "Uncategorized",
                "color": cat["category__color"] or "#6366f1",
                "icon": cat["category__icon"] or "➖",
                "amount": cat_sum,
                "pct": pct
            })

        # ----------------------------------------------------------------------
        # 3. Budget vs Actual limits per category
        # ----------------------------------------------------------------------
        budgets = Budget.objects.filter(user=user, month=month, year=year)
        budget_vs_actual_data = []

        for budget in budgets:
            category = budget.category
            actual_spent = base_qs.filter(category=category, type="expense").aggregate(sum=Sum("amount"))["sum"] or 0.0
            actual = float(actual_spent)
            limit = float(budget.limit_amount)
            remaining = max(0.0, limit - actual)

            pct_used = round((actual / limit) * 100, 2) if limit > 0.0 else 0.0
            if pct_used > 100.0:
                status_val = "over"
            elif pct_used >= 80.0:
                status_val = "warning"
            else:
                status_val = "safe"

            budget_vs_actual_data.append({
                "category_id": category.id,
                "category_name": category.name,
                "category_color": category.color,
                "category_icon": category.icon,
                "limit": limit,
                "actual": actual,
                "remaining": remaining,
                "pct_used": pct_used,
                "status": status_val
            })

        # ----------------------------------------------------------------------
        # 4. Global spending limit status
        # ----------------------------------------------------------------------
        monthly_limit = float(prefs.monthly_spending_limit) if prefs.monthly_spending_limit else 0.0
        global_remaining = max(0.0, monthly_limit - total_expense) if monthly_limit > 0.0 else 0.0
        global_pct_used = round((total_expense / monthly_limit) * 100, 2) if monthly_limit > 0.0 else 0.0

        if monthly_limit <= 0.0:
            global_status = "safe"
        elif global_pct_used > 100.0:
            global_status = "over"
        elif global_pct_used >= 80.0:
            global_status = "warning"
        else:
            global_status = "safe"

        global_limit_data = {
            "monthly_limit": monthly_limit,
            "total_spent": total_expense,
            "remaining": global_remaining,
            "pct_used": global_pct_used,
            "status": global_status
        }

        # ----------------------------------------------------------------------
        # 5. Upcoming unpaid bills in the next 7 days
        # ----------------------------------------------------------------------
        active_bills = Bill.objects.filter(user=user, is_active=True)
        seven_days_later = today + timedelta(days=7)
        upcoming_bills_data = []

        for bill in active_bills:
            # 5a. Determine the next due date based on the due_day
            try:
                due_date = date(today.year, today.month, bill.due_day)
            except ValueError:
                last_day = calendar.monthrange(today.year, today.month)[1]
                due_date = date(today.year, today.month, last_day)

            if today > due_date:
                next_month = today.month + 1
                year_val = today.year
                if next_month > 12:
                    next_month = 1
                    year_val += 1
                try:
                    due_date = date(year_val, next_month, bill.due_day)
                except ValueError:
                    last_day = calendar.monthrange(year_val, next_month)[1]
                    due_date = date(year_val, next_month, last_day)

            # 5b. Verify if a payment was logged for the current period
            is_paid = bill.payments.filter(
                paid_date__month=today.month,
                paid_date__year=today.year
            ).exists()

            if today <= due_date <= seven_days_later and not is_paid:
                upcoming_bills_data.append({
                    "id": bill.id,
                    "name": bill.name,
                    "amount": bill.amount,
                    "currency_code": bill.currency_code,
                    "due_day": bill.due_day,
                    "frequency": bill.frequency,
                    "next_due_date": due_date,
                    "is_paid_this_period": is_paid
                })

        # ----------------------------------------------------------------------
        # 6. Savings Goals and their progress/track status
        # ----------------------------------------------------------------------
        goals = SavingsGoal.objects.filter(user=user)
        goals_data = []

        for goal in goals:
            total_saved = float(goal.total_saved)
            target = float(goal.target_amount)
            progress_pct = min(100.0, round((total_saved / target) * 100, 2)) if target > 0.0 else 0.0

            is_on_track = True
            if goal.deadline and total_saved < target:
                created_date = goal.created_at.date()
                days_total = (goal.deadline - created_date).days
                if days_total > 0:
                    days_elapsed = max(0, (today - created_date).days)
                    expected_saved = (days_elapsed / days_total) * target
                    is_on_track = total_saved >= expected_saved

            goals_data.append({
                "id": goal.id,
                "name": goal.name,
                "target_amount": goal.target_amount,
                "total_saved": total_saved,
                "progress_pct": progress_pct,
                "is_on_track": is_on_track,
                "currency_code": goal.currency_code
            })

        # ----------------------------------------------------------------------
        # 7. Month-over-month percentage changes in income and expenses
        # ----------------------------------------------------------------------
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year = year - 1

        prev_base_qs = Transaction.objects.filter(
            user=user,
            date__month=prev_month,
            date__year=prev_year,
            currency_code=currency,
            is_deleted=False
        )

        prev_income = float(prev_base_qs.filter(type="income").aggregate(sum=Sum("amount"))["sum"] or 0.0)
        prev_expense = float(prev_base_qs.filter(type="expense").aggregate(sum=Sum("amount"))["sum"] or 0.0)

        if prev_income == 0.0:
            income_change_pct = 100.0 if total_income > 0.0 else 0.0
        else:
            income_change_pct = round(((total_income - prev_income) / prev_income) * 100, 2)

        if prev_expense == 0.0:
            expense_change_pct = 100.0 if total_expense > 0.0 else 0.0
        else:
            expense_change_pct = round(((total_expense - prev_expense) / prev_expense) * 100, 2)

        mom_change_data = {
            "income_change_pct": income_change_pct,
            "expense_change_pct": expense_change_pct
        }

        # ----------------------------------------------------------------------
        # Assemble Response
        # ----------------------------------------------------------------------
        dashboard_data = {
            "month": month,
            "year": year,
            "currency": currency,
            "summary": {
                "total_income": total_income,
                "total_expense": total_expense,
                "net": net,
                "savings_rate_pct": savings_rate_pct
            },
            "spending_by_category": spending_by_category_data,
            "budget_vs_actual": budget_vs_actual_data,
            "global_limit": global_limit_data,
            "upcoming_bills": upcoming_bills_data,
            "goals": goals_data,
            "mom_change": mom_change_data
        }

        serializer = DashboardResponseSerializer(dashboard_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
