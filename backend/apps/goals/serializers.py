"""Goals serializers."""

from datetime import date
from rest_framework import serializers
from apps.goals.models import SavingsGoal, GoalContribution

class SavingsGoalSerializer(serializers.ModelSerializer):
    total_saved = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    progress_pct = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    monthly_required = serializers.SerializerMethodField()
    is_on_track = serializers.SerializerMethodField()

    class Meta:
        model = SavingsGoal
        fields = (
            "id",
            "name",
            "description",
            "target_amount",
            "currency_code",
            "deadline",
            "created_at",
            "total_saved",
            "remaining",
            "progress_pct",
            "days_remaining",
            "monthly_required",
            "is_on_track",
        )
        read_only_fields = ("id", "created_at")

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Target amount must be greater than zero.")
        return value

    def get_total_saved(self, obj):
        return float(obj.total_saved)

    def get_remaining(self, obj):
        target = float(obj.target_amount)
        saved = float(obj.total_saved)
        return max(0.0, target - saved)

    def get_progress_pct(self, obj):
        target = float(obj.target_amount)
        saved = float(obj.total_saved)
        if target <= 0:
            return 0.0
        return min(100.0, round((saved / target) * 100, 2))

    def get_days_remaining(self, obj):
        if not obj.deadline:
            return None
        today = date.today()
        return max(0, (obj.deadline - today).days)

    def get_monthly_required(self, obj):
        target = float(obj.target_amount)
        saved = float(obj.total_saved)
        remaining = target - saved
        if remaining <= 0:
            return 0.0

        if not obj.deadline:
            return None

        today = date.today()
        # Calculate number of calendar months remaining
        months = (obj.deadline.year - today.year) * 12 + (obj.deadline.month - today.month)
        months = max(1, months)
        return round(remaining / months, 2)

    def get_is_track_value(self, obj):
        # Internal helper
        if not obj.deadline:
            return True
        saved = float(obj.total_saved)
        target = float(obj.target_amount)
        if saved >= target:
            return True

        created_date = obj.created_at.date()
        today = date.today()
        
        days_total = (obj.deadline - created_date).days
        if days_total <= 0:
            return True

        days_elapsed = (today - created_date).days
        days_elapsed = max(0, days_elapsed)

        expected_saved = (days_elapsed / days_total) * target
        return saved >= expected_saved

    def get_is_on_track(self, obj):
        return self.get_is_track_value(obj)


class GoalContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalContribution
        fields = ("id", "goal", "amount", "date", "note", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Contribution amount must be greater than zero.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        goal = attrs.get("goal")
        if goal and goal.user != user:
            raise serializers.ValidationError({"goal": "Selected goal does not exist or belong to your profile."})
        return attrs
