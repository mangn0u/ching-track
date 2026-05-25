"""Bills serializers stub."""

# TODO Day 5: Implement the following serializers
#
# BillSerializer
#   Fields: id, name, amount, currency_code, due_day, frequency, is_active
#   Computed (read-only): next_due_date, is_paid_this_period
#   Validate: due_day in range(1, 32), amount > 0
#
# BillPaymentSerializer
#   Fields: id, bill, paid_date, amount_paid, note, created_at
