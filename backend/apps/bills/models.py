"""Bill and BillPayment models."""

from django.conf import settings
from django.db import models


class Bill(models.Model):
    FREQUENCY_CHOICES = [
        ("monthly", "Monthly"),
        ("weekly", "Weekly"),
        ("once", "One-time"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bills"
    )
    name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency_code = models.CharField(max_length=3, default="KES")
    due_day = models.IntegerField()          # day of month (1-31)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="monthly")
    is_active = models.BooleanField(default=True)   # False = soft deleted
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_day"]

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class BillPayment(models.Model):
    """
    Records each time a bill is marked as paid.
    One record per billing period per bill.
    """

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="payments")
    paid_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_date"]

    def __str__(self):
        return f"Payment({self.bill.name} on {self.paid_date})"
