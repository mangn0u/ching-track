"""Transactions serializers stub."""

# TODO Day 3: Implement the following serializers
#
# CategorySerializer
#   Fields: id, name, type, color, icon, is_default
#
# TransactionListSerializer (lightweight — for list view)
#   Fields: id, type, amount, currency_code, category_name, category_color, date, note
#
# TransactionDetailSerializer (full — for retrieve/create/update)
#   Fields: all fields including mpesa_ref, created_at, updated_at
#
# TransactionCreateSerializer
#   Validate: amount > 0, category belongs to request.user
