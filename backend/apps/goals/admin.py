from django.contrib import admin

from .models import GoalContribution, SavingsGoal


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "target_amount", "currency_code", "deadline"]
    search_fields = ["name", "user__email"]


@admin.register(GoalContribution)
class GoalContributionAdmin(admin.ModelAdmin):
    list_display = ["goal", "amount", "date"]
    date_hierarchy = "date"
