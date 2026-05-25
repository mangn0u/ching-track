"""Goals serializers stub."""

# TODO Day 6: Implement the following serializers
#
# SavingsGoalSerializer
#   Fields: id, name, description, target_amount, currency_code, deadline, created_at
#   Computed (read-only):
#     - total_saved        (sum of contributions)
#     - remaining          (target_amount - total_saved)
#     - progress_pct       (total_saved / target_amount * 100)
#     - days_remaining     (deadline - today).days
#     - monthly_required   (remaining / months_to_deadline)
#     - is_on_track        (total_saved >= expected_at_this_point)
#
# GoalContributionSerializer
#   Fields: id, goal, amount, date, note, created_at
#   Validate: amount > 0
