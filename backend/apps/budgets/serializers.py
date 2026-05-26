"""Budgets serializers."""

from rest_framework import serializers
from apps.budgets.models import UserPreferences, Budget
from apps.transactions.models import Category

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ("currency", "monthly_spending_limit", "updated_at")
        read_only_fields = ("updated_at",)


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_color = serializers.CharField(source="category.color", read_only=True)

    class Meta:
        model = Budget
        fields = ("id", "category", "category_name", "category_color", "month", "year", "limit_amount")
        read_only_fields = ("id",)

    def validate_limit_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Limit amount must be greater than zero.")
        return value

    def validate_month(self, value):
        if not (1 <= value <= 12):
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        category = attrs.get("category")

        # Category must belong to the user
        if category and category.user != user:
            raise serializers.ValidationError({"category": "Selected category does not exist or belong to your profile."})

        # Category must be an expense type
        if category and category.type != "expense":
            raise serializers.ValidationError({"category": "Budgets can only be set on expense categories."})

        return attrs


class BudgetVsActualSerializer(serializers.Serializer):
    category_id = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(read_only=True)
    category_color = serializers.CharField(read_only=True)
    category_icon = serializers.CharField(read_only=True)
    limit = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    actual = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    pct_used = serializers.FloatField(read_only=True)
    status = serializers.CharField(read_only=True)


class SpendingStatusSerializer(serializers.Serializer):
    monthly_limit = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_spent = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    pct_used = serializers.FloatField(read_only=True)
    status = serializers.CharField(read_only=True)
