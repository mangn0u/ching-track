"""Analytics serializers."""

from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)
    savings_rate_pct = serializers.FloatField()


class CategorySpendingSerializer(serializers.Serializer):
    category = serializers.CharField()
    color = serializers.CharField()
    icon = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    pct = serializers.FloatField()


class BudgetVsActualSnapshotSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    category_color = serializers.CharField()
    category_icon = serializers.CharField()
    limit = serializers.DecimalField(max_digits=14, decimal_places=2)
    actual = serializers.DecimalField(max_digits=14, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=14, decimal_places=2)
    pct_used = serializers.FloatField()
    status = serializers.CharField()


class GlobalLimitSnapshotSerializer(serializers.Serializer):
    monthly_limit = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=14, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=14, decimal_places=2)
    pct_used = serializers.FloatField()
    status = serializers.CharField()


class UpcomingBillSnapshotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency_code = serializers.CharField()
    due_day = serializers.IntegerField()
    frequency = serializers.CharField()
    next_due_date = serializers.DateField()
    is_paid_this_period = serializers.BooleanField()


class GoalSnapshotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    target_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_saved = serializers.DecimalField(max_digits=14, decimal_places=2)
    progress_pct = serializers.FloatField()
    is_on_track = serializers.BooleanField()
    currency_code = serializers.CharField()


class MoMChangeSerializer(serializers.Serializer):
    income_change_pct = serializers.FloatField()
    expense_change_pct = serializers.FloatField()


class MonthlyTrendSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    income = serializers.DecimalField(max_digits=14, decimal_places=2)
    expense = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)


class TopCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    color = serializers.CharField()
    icon = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)


class TrendsResponseSerializer(serializers.Serializer):
    currency = serializers.CharField()
    monthly = MonthlyTrendSerializer(many=True)
    total_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)
    top_categories = TopCategorySerializer(many=True)


class DashboardResponseSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    currency = serializers.CharField()
    summary = DashboardSummarySerializer()
    spending_by_category = CategorySpendingSerializer(many=True)
    budget_vs_actual = BudgetVsActualSnapshotSerializer(many=True)
    global_limit = GlobalLimitSnapshotSerializer()
    upcoming_bills = UpcomingBillSnapshotSerializer(many=True)
    goals = GoalSnapshotSerializer(many=True)
    mom_change = MoMChangeSerializer()
