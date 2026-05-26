"""Accounts serializers — register, login, profile, password."""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import CustomUser, EmailVerificationToken

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password", "password_confirm", "first_name", "last_name", "phone_number", "mpesa_phone")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data.get("phone_number", ""),
            mpesa_phone=validated_data.get("mpesa_phone", None)
        )
        # Create email verification token
        token_obj = EmailVerificationToken.objects.create(user=user)
        
        # Send verification email (will print to terminal console in development)
        from django.core.mail import send_mail
        from django.conf import settings
        
        verify_url = f"{settings.FRONTEND_URL}/verify-email/{token_obj.token}/"
        send_mail(
            subject="Verify Your Ching-Track Account",
            message=f"Hi {user.first_name},\n\nPlease verify your account by clicking the link: {verify_url}\n\nThanks,\nChing-Track Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "phone_number", "mpesa_phone", "is_email_verified", "date_joined")
        read_only_fields = ("id", "email", "is_email_verified", "date_joined")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})
        return attrs
