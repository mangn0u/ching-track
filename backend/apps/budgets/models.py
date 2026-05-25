"""
Budget and UserPreferences models.
"""

from django.conf import settings
from django.db import models


class UserPreferences(models.Model):
    """
    Per-user settings: preferred currency and global monthly spending limit.
    Created automatically via signal when a user registers.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferences"
    )
    currency = models.CharField(max_length=3, default="KES")
    monthly_spending_limit = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Preferences"
        verbose_name_plural = "User Preferences"

    def __str__(self):
        return f"Preferences({self.user.email})"


class Budget(models.Model):
    """
    A monthly spend limit set by a user for a specific category.
    Unique per user + category + month + year combination.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets"
    )
    category = models.ForeignKey(
        "transactions.Category", on_delete=models.CASCADE, related_name="budgets"
    )
    month = models.IntegerField()   # 1-12
    year = models.IntegerField()
    limit_amount = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "category", "month", "year")
        ordering = ["category__name"]

    def __str__(self):
        return f"Budget({self.user.email} | {self.category.name} | {self.month}/{self.year})"
