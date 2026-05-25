"""Budgets views stub."""

# TODO Day 4: Implement the following views
#
# BudgetListCreateView      GET/POST /api/v1/budgets/
#   - GET: filter by ?month=&year=
#   - POST: upsert — update if exists, create if not
#
# BudgetDeleteView          DELETE /api/v1/budgets/:id/
#
# BudgetVsActualView        GET /api/v1/budgets/vs-actual/
#   - Query: ?month=&year=
#   - For each budget: compute actual spend from Transaction queryset
#   - Return list with status flags
#
# UserPreferencesView       GET/PUT /api/v1/preferences/
#
# SpendingStatusView        GET /api/v1/preferences/spending-status/
#   - Compare monthly_spending_limit vs sum of expense transactions this month
