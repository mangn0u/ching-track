"""Bills serializers."""

from datetime import date, timedelta
from rest_framework import serializers
from apps.bills.models import Bill, BillPayment

class BillSerializer(serializers.ModelSerializer):
    next_due_date = serializers.SerializerMethodField()
    is_paid_this_period = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = (
            "id",
            "name",
            "amount",
            "currency_code",
            "due_day",
            "frequency",
            "is_active",
            "next_due_date",
            "is_paid_this_period",
        )
        read_only_fields = ("id", "is_active")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_due_day(self, value):
        if not (1 <= value <= 31):
            raise serializers.ValidationError("Due day must be between 1 and 31.")
        return value

    def get_next_due_date(self, obj):
        today = date.today()
        # Find next occurrence of the due day
        try:
            due_date = date(today.year, today.month, obj.due_day)
        except ValueError:
            # Handle months with fewer days than due_day (e.g. Feb 30)
            # Roll over to the last day of the month
            import calendar
            last_day = calendar.monthrange(today.year, today.month)[1]
            due_date = date(today.year, today.month, last_day)

        if today > due_date:
            # Due date has passed in the current month, next is next month
            next_month = today.month + 1
            year = today.year
            if next_month > 12:
                next_month = 1
                year += 1
            try:
                due_date = date(year, next_month, obj.due_day)
            except ValueError:
                import calendar
                last_day = calendar.monthrange(year, next_month)[1]
                due_date = date(year, next_month, last_day)

        return due_date

    def get_is_paid_this_period(self, obj):
        today = date.today()
        # Checks if a payment was already logged for the current month and year
        return obj.payments.filter(
            paid_date__month=today.month,
            paid_date__year=today.year
        ).exists()


class BillPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillPayment
        fields = ("id", "bill", "paid_date", "amount_paid", "note", "created_at")
        read_only_fields = ("id", "created_at")
