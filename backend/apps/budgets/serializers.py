"""Budgets serializers stub."""

# TODO Day 4: Implement the following serializers
#
# UserPreferencesSerializer
#   Fields: currency, monthly_spending_limit, updated_at
#
# BudgetSerializer
#   Fields: id, category, category_name, month, year, limit_amount
#   Validate: limit_amount > 0, month in range(1,13)
#
# BudgetVsActualSerializer (read-only, computed)
#   Fields: category_id, category_name, category_color,
#           limit, actual, remaining, pct_used, status
#   status: "safe" | "warning" | "over"
#
# SpendingStatusSerializer (read-only, computed)
#   Fields: monthly_limit, total_spent, remaining, pct_used, status
