"""
Category and Transaction models.
"""

from django.conf import settings
from django.db import models


class Category(models.Model):
    TRANSACTION_TYPES = [("income", "Income"), ("expense", "Expense")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    color = models.CharField(max_length=7, default="#6366f1")   # hex color
    icon = models.CharField(max_length=50, blank=True)           # emoji or icon name
    is_default = models.BooleanField(default=False)              # system-seeded categories
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "name", "type")
        ordering = ["type", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.type})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [("income", "Income"), ("expense", "Expense")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="transactions"
    )
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency_code = models.CharField(max_length=3, default="KES")
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)

    # M-Pesa SMS parsing — populated when transaction is imported from SMS
    mpesa_ref = models.CharField(max_length=20, blank=True)
    mpesa_raw_sms = models.TextField(blank=True)

    # Soft delete — keeps audit trail
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "type"]),
            models.Index(fields=["user", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.type} {self.amount} {self.currency_code} on {self.date}"
