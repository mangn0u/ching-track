"""SavingsGoal and GoalContribution models."""

from django.conf import settings
from django.db import models


class SavingsGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency_code = models.CharField(max_length=3, default="KES")
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Goal({self.name} | {self.user.email})"

    @property
    def total_saved(self):
        """Sum of all contributions. Always computed — never stored."""
        result = self.contributions.aggregate(total=models.Sum("amount"))
        return result["total"] or 0


class GoalContribution(models.Model):
    """A single deposit towards a savings goal."""

    goal = models.ForeignKey(
        SavingsGoal, on_delete=models.CASCADE, related_name="contributions"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Contribution({self.goal.name} | {self.amount} on {self.date})"
