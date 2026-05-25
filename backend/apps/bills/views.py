"""Bills views stub."""

# TODO Day 5: Implement the following views
#
# BillListCreateView    GET/POST /api/v1/bills/
#   - GET: filter ?active=true, annotate is_paid_this_period
#
# BillDetailView        GET/PUT/DELETE /api/v1/bills/:id/
#   - DELETE: soft delete (is_active=False), not a real DB delete
#
# BillPayView           POST /api/v1/bills/:id/pay/
#   - Check: no BillPayment exists for this bill in current period → 400 if duplicate
#   - Create BillPayment record
#   - Optionally create matching expense Transaction
#
# UpcomingBillsView     GET /api/v1/bills/upcoming/
#   - Return active bills where due_day falls within next 7 days
#   - Annotate each with is_paid_this_period
