"""Budgets views — lists, upserting, preference settings, and limit computations."""

from datetime import date
from django.db.models import Sum
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.budgets.models import UserPreferences, Budget
from apps.transactions.models import Transaction, Category
from apps.budgets.serializers import (
    UserPreferencesSerializer,
    BudgetSerializer,
    BudgetVsActualSerializer,
    SpendingStatusSerializer,
)
from core.permissions import IsOwner

# ------------------------------------------------------------------------------
# Preferences Views
# ------------------------------------------------------------------------------
class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT /api/v1/preferences/
    View and edit current user's general preferences.
    """
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Always return the authenticated user's preferences (created via signal on sign-up)
        obj, created = UserPreferences.objects.get_or_create(user=self.request.user)
        return obj


class SpendingStatusView(APIView):
    """
    GET /api/v1/preferences/spending-status/
    Calculates the user's global spending limit status for the current/selected month.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        prefs, _ = UserPreferences.objects.get_or_create(user=user)
        
        # Determine month and year filters
        today = date.today()
        month = request.query_params.get("month", today.month)
        year = request.query_params.get("year", today.year)
        
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Month and Year must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        # Sum of all expenses in the month
        total_spent = Transaction.objects.filter(
            user=user,
            type="expense",
            date__month=month,
            date__year=year,
            currency_code=prefs.currency,
            is_deleted=False
        ).aggregate(sum=Sum("amount"))["sum"] or 0
        
        total_spent = float(total_spent)
        monthly_limit = float(prefs.monthly_spending_limit) if prefs.monthly_spending_limit else 0.0
        remaining = max(0.0, monthly_limit - total_spent) if monthly_limit > 0 else 0.0
        
        # Calculate status
        pct_used = round((total_spent / monthly_limit) * 100, 2) if monthly_limit > 0 else 0.0
        if monthly_limit <= 0:
            status_val = "safe"
        elif pct_used > 100:
            status_val = "over"
        elif pct_used >= 80:
            status_val = "warning"
        else:
            status_val = "safe"

        serializer = SpendingStatusSerializer({
            "monthly_limit": monthly_limit,
            "total_spent": total_spent,
            "remaining": remaining,
            "pct_used": pct_used,
            "status": status_val
        })
        return Response(serializer.data, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------------
# Budget Views
# ------------------------------------------------------------------------------
class BudgetListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/budgets/
    POST /api/v1/budgets/
    List budgets or dynamically upsert (create or update) a budget limit.
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Budget.objects.filter(user=user)
        
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
            
        return queryset

    def create(self, request, *args, **kwargs):
        # Override standard create to support seamless upserting (create or update)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        category = serializer.validated_data["category"]
        month = serializer.validated_data["month"]
        year = serializer.validated_data["year"]
        limit_amount = serializer.validated_data["limit_amount"]

        # Perform the upsert
        budget, created = Budget.objects.update_or_create(
            user=user,
            category=category,
            month=month,
            year=year,
            defaults={"limit_amount": limit_amount}
        )
        
        response_serializer = self.get_serializer(budget)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(response_serializer.data, status=status_code)


class BudgetDetailView(generics.DestroyAPIView):
    """
    DELETE /api/v1/budgets/:id/
    Remove a specific budget limit.
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


class BudgetVsActualView(APIView):
    """
    GET /api/v1/budgets/vs-actual/
    Returns category-wise budget vs actual expenses for the selected month/year.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = date.today()
        
        # Preferences for default currency
        prefs, _ = UserPreferences.objects.get_or_create(user=user)
        currency = request.query_params.get("currency", prefs.currency)

        month = request.query_params.get("month", today.month)
        year = request.query_params.get("year", today.year)
        
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Month and Year must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        # Get all budgets for that month
        budgets = Budget.objects.filter(user=user, month=month, year=year)
        results = []

        for budget in budgets:
            category = budget.category
            
            # Sum up transactions in this category for that month
            actual_spent = Transaction.objects.filter(
                user=user,
                category=category,
                type="expense",
                date__month=month,
                date__year=year,
                currency_code=currency,
                is_deleted=False
            ).aggregate(sum=Sum("amount"))["sum"] or 0
            
            actual = float(actual_spent)
            limit = float(budget.limit_amount)
            remaining = max(0.0, limit - actual)
            
            # Pct & status
            pct_used = round((actual / limit) * 100, 2) if limit > 0 else 0.0
            if pct_used > 100:
                status_val = "over"
            elif pct_used >= 80:
                status_val = "warning"
            else:
                status_val = "safe"

            results.append({
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

        serializer = BudgetVsActualSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
