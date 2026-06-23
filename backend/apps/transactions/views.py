"""Transactions views — CRUD, soft delete, and summaries."""

from datetime import date
from django.db.models import Sum, Q
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.transactions.models import Category, Transaction
from apps.transactions.serializers import (
    CategorySerializer,
    TransactionListSerializer,
    TransactionDetailSerializer,
)
from core.permissions import IsOwner

# ------------------------------------------------------------------------------
# Category Views
# ------------------------------------------------------------------------------
class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/categories/
    POST /api/v1/categories/
    List and create user-scoped categories.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.filter(user=user)
        cat_type = self.request.query_params.get("type")
        if cat_type:
            queryset = queryset.filter(type=cat_type)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_default=False)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/categories/:id/
    Retrieve, update, or delete a custom category.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default:
            return Response(
                {"error": "You cannot edit system-seeded default categories."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default:
            return Response(
                {"error": "You cannot delete system-seeded default categories."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Block if transactions are linked
        if instance.transactions.filter(is_deleted=False).exists():
            return Response(
                {"error": "Cannot delete category because active transactions are linked to it."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


# ------------------------------------------------------------------------------
# Transaction Views
# ------------------------------------------------------------------------------
class TransactionListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/transactions/
    POST /api/v1/transactions/
    List and create user-scoped transactions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TransactionDetailSerializer
        return TransactionListSerializer

    def get_queryset(self):
        user = self.request.user
        # Exclude soft-deleted transactions
        queryset = Transaction.objects.filter(user=user, is_deleted=False)

        # Filters
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        tx_type = self.request.query_params.get("type")
        category_id = self.request.query_params.get("category")
        currency = self.request.query_params.get("currency")

        if month:
            queryset = queryset.filter(date__month=month)
        if year:
            queryset = queryset.filter(date__year=year)
        if tx_type:
            queryset = queryset.filter(type=tx_type)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if currency:
            queryset = queryset.filter(currency_code=currency)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/v1/transactions/:id/
    Retrieve, update, or soft-delete a transaction.
    """
    serializer_class = TransactionDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user, is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete instead of hard delete
        instance.is_deleted = True
        instance.save()
        return Response({"message": "Transaction soft-deleted successfully."}, status=status.HTTP_200_OK)


class TransactionSummaryView(APIView):
    """
    GET /api/v1/transactions/summary/
    Returns month-specific aggregates: {total_income, total_expense, net, savings_rate_pct, by_category[]}
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = date.today()

        # Extract filters with defaults
        month = request.query_params.get("month", today.month)
        year = request.query_params.get("year", today.year)
        currency = request.query_params.get("currency", "KES")

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Month and Year must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        # Base filter
        base_qs = Transaction.objects.filter(
            user=user, date__month=month, date__year=year, currency_code=currency, is_deleted=False
        )

        # Totals
        total_income = base_qs.filter(type="income").aggregate(sum=Sum("amount"))["sum"] or 0
        total_expense = base_qs.filter(type="expense").aggregate(sum=Sum("amount"))["sum"] or 0
        
        total_income = float(total_income)
        total_expense = float(total_expense)
        net = total_income - total_expense

        # Savings rate
        savings_rate = 0.0
        if total_income > 0 and net > 0:
            savings_rate = round((net / total_income) * 100, 2)

        # Spending by category (for expenses)
        by_category = []
        category_spending = (
            base_qs.filter(type="expense")
            .values("category__name", "category__color", "category__icon")
            .annotate(sum=Sum("amount"))
            .order_by("-sum")
        )

        for cat in category_spending:
            cat_sum = float(cat["sum"])
            pct = round((cat_sum / total_expense) * 100, 2) if total_expense > 0 else 0.0
            by_category.append({
                "category": cat["category__name"] or "Uncategorized",
                "color": cat["category__color"] or "#6366f1",
                "icon": cat["category__icon"] or "➖",
                "amount": f"{cat_sum:.2f}",
                "pct": pct
            })

        return Response({
            "month": month,
            "year": year,
            "currency": currency,
            "total_income": f"{total_income:.2f}",
            "total_expense": f"{total_expense:.2f}",
            "net": f"{net:.2f}",
            "savings_rate_pct": savings_rate,
            "by_category": by_category
        }, status=status.HTTP_200_OK)
