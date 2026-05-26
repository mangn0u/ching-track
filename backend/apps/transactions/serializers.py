"""Transactions serializers."""

from rest_framework import serializers
from apps.transactions.models import Category, Transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "type", "color", "icon", "is_default")
        read_only_fields = ("id", "is_default")

    def validate(self, attrs):
        user = self.context["request"].user
        name = attrs.get("name")
        type_ = attrs.get("type")
        
        # Check uniqueness per user-name-type
        if Category.objects.filter(user=user, name=name, type=type_).exists():
            raise serializers.ValidationError("A category with this name and type already exists.")
        return attrs


class TransactionListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_color = serializers.CharField(source="category.color", read_only=True)
    category_icon = serializers.CharField(source="category.icon", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "type",
            "amount",
            "currency_code",
            "category",
            "category_name",
            "category_color",
            "category_icon",
            "date",
            "note",
            "mpesa_ref",
        )


class TransactionDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_color = serializers.CharField(source="category.color", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "category",
            "category_name",
            "category_color",
            "type",
            "amount",
            "currency_code",
            "date",
            "note",
            "mpesa_ref",
            "mpesa_raw_sms",
            "is_deleted",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "is_deleted", "created_at", "updated_at")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        category = attrs.get("category")
        type_ = attrs.get("type")

        # Category must belong to the user
        if category and category.user != user:
            raise serializers.ValidationError({"category": "Selected category does not exist or belong to your profile."})

        # Category type must match transaction type
        if category and category.type != type_:
            raise serializers.ValidationError({"category": f"Selected category type must be '{type_}'."})

        return attrs
