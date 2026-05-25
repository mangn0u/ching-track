"""Transactions views stub."""

# TODO Day 3: Implement the following views
#
# CategoryListCreateView    GET/POST /api/v1/categories/
# CategoryDetailView        PUT/DELETE /api/v1/categories/:id/
#
# TransactionListCreateView GET/POST /api/v1/transactions/
#   - Filter by: month, year, type, category
#   - Exclude soft-deleted: is_deleted=False
#
# TransactionDetailView     GET/PUT/PATCH/DELETE /api/v1/transactions/:id/
#   - DELETE sets is_deleted=True (soft delete)
#
# TransactionSummaryView    GET /api/v1/transactions/summary/
#   - Returns: {total_income, total_expense, net, savings_rate_pct, by_category[]}
