"""Bills views — CRUD, soft delete, payment processing, and upcoming bills."""

from datetime import date, timedelta
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.bills.models import Bill, BillPayment
from apps.transactions.models import Transaction, Category
from apps.bills.serializers import BillSerializer, BillPaymentSerializer

class BillListCreateView(generics.ListCreateView):
    """
    GET /api/v1/bills/
    POST /api/v1/bills/
    List active bills or create new recurring bills.
    """
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Bill.objects.filter(user=user)
        
        # Filter active by default
        active = self.request.query_params.get("active", "true")
        if active.lower() == "true":
            queryset = queryset.filter(is_active=True)
        elif active.lower() == "false":
            queryset = queryset.filter(is_active=False)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/bills/:id/
    Retrieve, edit, or soft-delete a bill.
    """
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bill.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "Bill soft-deleted successfully."}, status=status.HTTP_200_OK)


class BillPayView(APIView):
    """
    POST /api/v1/bills/:id/pay/
    Record a bill payment and auto-generate an expense transaction.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        user = request.user
        bill = generics.get_object_or_404(Bill, id=pk, user=user, is_active=True)
        today = date.today()

        # Check if already paid this period
        already_paid = bill.payments.filter(
            paid_date__month=today.month,
            paid_date__year=today.year
        ).exists()

        if already_paid:
            return Response(
                {"error": "This bill has already been marked as paid for this month."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create BillPayment
        note = request.data.get("note", f"Automatic payment for {bill.name}")
        amount_paid = request.data.get("amount_paid", bill.amount)

        payment = BillPayment.objects.create(
            bill=bill,
            paid_date=today,
            amount_paid=amount_paid,
            note=note
        )

        # Auto-create matching expense Transaction
        # Find default "Utilities" or "Other Expense" category for the user
        category = Category.objects.filter(user=user, type="expense", name="Utilities").first()
        if not category:
            category = Category.objects.filter(user=user, type="expense", name="Other Expense").first()

        Transaction.objects.create(
            user=user,
            category=category,
            type="expense",
            amount=amount_paid,
            currency_code=bill.currency_code,
            date=today,
            note=f"Paid Bill: {bill.name}. {note}",
        )

        serializer = BillPaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpcomingBillsView(APIView):
    """
    GET /api/v1/bills/upcoming/
    Returns active bills due in the next 7 days that are not yet paid.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        active_bills = Bill.objects.filter(user=user, is_active=True)
        today = date.today()
        seven_days_later = today + timedelta(days=7)

        upcoming_bills = []
        
        for bill in active_bills:
            serializer = BillSerializer(bill, context={"request": request})
            due_date = serializer.get_next_due_date(bill)
            is_paid = serializer.get_is_paid_this_period(bill)
            
            # Check if next_due_date falls within the 7-day range and is not paid
            if today <= due_date <= seven_days_later and not is_paid:
                data = serializer.data
                upcoming_bills.append(data)

        return Response(upcoming_bills, status=status.HTTP_200_OK)
