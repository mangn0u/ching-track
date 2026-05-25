from django.contrib import admin

from .models import Budget, UserPreferences


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ["user", "currency", "monthly_spending_limit", "updated_at"]


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["user", "category", "month", "year", "limit_amount"]
    list_filter = ["year", "month"]
    search_fields = ["user__email", "category__name"]
