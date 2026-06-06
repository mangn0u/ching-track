"""Accounts views — register, login, logout, verify, reset password."""

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import CustomUser, EmailVerificationToken, PasswordResetToken
from apps.accounts.serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

# ------------------------------------------------------------------------------
# Login with Email Verification Check
# ------------------------------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_email_verified:
            raise serializers.ValidationError({"error": "Your email address is not verified yet."})

        data["user"] = UserProfileSerializer(self.user).data
        return data


@method_decorator(ratelimit(key="ip", rate="5/m", block=True), name="dispatch")
class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    Returns access, refresh tokens and user profile if email is verified.
    """
    serializer_class = CustomTokenObtainPairSerializer


# ------------------------------------------------------------------------------
# Register and Verify Views
# ------------------------------------------------------------------------------
class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Registers a new user and triggers verification email.
    """
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class VerifyEmailView(APIView):
    """
    GET /api/v1/auth/verify-email/<token>/
    Activates user account if verification token is valid.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, token, *args, **kwargs):
        token_obj = get_object_or_404(EmailVerificationToken, token=token)
        user = token_obj.user
        user.is_email_verified = True
        user.save()
        token_obj.delete()
        return Response({"message": "Email verified successfully! You can now log in."}, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------------
# Profile & Logout Views
# ------------------------------------------------------------------------------
class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Blacklists the refresh token to end the session.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid or missing refresh token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT /api/v1/auth/me/
    View and edit current user's profile details.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    POST /api/v1/auth/change-password/
    Updates user's password after validating old password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response({"old_password": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------
# Password Reset Views
# ------------------------------------------------------------------------------
class ForgotPasswordView(APIView):
    """
    POST /api/v1/auth/forgot-password/
    Sends password reset email if user exists.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"email": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(email=email).first()
        if user:
            reset_token = PasswordResetToken.objects.create(user=user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}/"
            send_mail(
                subject="Reset Your Ching-Track Password",
                message=f"Hi {user.first_name},\n\nYou requested a password reset. Reset your password by clicking the link: {reset_url}\n\nThanks,\nChing-Track Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        
        # Always return 200 to prevent user enumeration
        return Response({"message": "If this email is registered, a password reset link has been sent."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    POST /api/v1/auth/reset-password/<token>/
    Resets user password if token is valid.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, token, *args, **kwargs):
        reset_token = get_object_or_404(PasswordResetToken, token=token, is_used=False)
        password = request.data.get("password")
        if not password:
            return Response({"password": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = reset_token.user
        user.set_password(password)
        user.save()
        
        reset_token.is_used = True
        reset_token.save()
        return Response({"message": "Password reset successfully!"}, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------------
# GDPR Compliance Views
# ------------------------------------------------------------------------------
class ExportDataView(APIView):
    """
    GET /api/v1/auth/export-data/
    Export all user data in JSON format for GDPR compliance.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Gather all related data
        # We can dynamically serialize transactions, budgets, bills, goals
        from apps.transactions.models import Transaction, Category
        from apps.budgets.models import Budget, UserPreferences
        from apps.bills.models import Bill
        from apps.goals.models import SavingsGoal
        
        profile = UserProfileSerializer(user).data
        
        # Categories
        categories = list(Category.objects.filter(user=user).values("name", "type", "color", "icon", "is_default"))
        
        # Transactions
        transactions = list(Transaction.objects.filter(user=user).values(
            "category__name", "type", "amount", "currency_code", "date", "note", "mpesa_ref", "is_deleted"
        ))
        
        # Budgets
        budgets = list(Budget.objects.filter(user=user).values("category__name", "month", "year", "limit_amount"))
        
        # Preferences
        prefs_obj = UserPreferences.objects.filter(user=user).first()
        preferences = {
            "currency": prefs_obj.currency if prefs_obj else "KES",
            "monthly_spending_limit": str(prefs_obj.monthly_spending_limit) if prefs_obj and prefs_obj.monthly_spending_limit else None
        }
        
        # Bills
        bills = []
        for bill in Bill.objects.filter(user=user):
            payments = list(bill.payments.values("paid_date", "amount_paid"))
            bills.append({
                "name": bill.name,
                "amount": str(bill.amount),
                "due_day": bill.due_day,
                "frequency": bill.frequency,
                "is_active": bill.is_active,
                "payments": payments
            })
            
        # Goals
        goals = []
        for goal in SavingsGoal.objects.filter(user=user):
            contributions = list(goal.contributions.values("amount", "date", "note"))
            goals.append({
                "name": goal.name,
                "target_amount": str(goal.target_amount),
                "deadline": str(goal.deadline) if goal.deadline else None,
                "currency_code": goal.currency_code,
                "contributions": contributions
            })

        data = {
            "profile": profile,
            "preferences": preferences,
            "categories": categories,
            "transactions": transactions,
            "budgets": budgets,
            "bills": bills,
            "goals": goals
        }
        
        return Response(data, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    """
    DELETE /api/v1/auth/delete-account/
    Hard delete user account and all cascade data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()  # Cascade deletes all foreign key objects
        return Response({"message": "Your account has been deleted permanently."}, status=status.HTTP_200_OK)
