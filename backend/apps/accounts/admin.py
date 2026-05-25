from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, EmailVerificationToken, PasswordResetToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["email", "first_name", "last_name", "is_email_verified", "date_joined"]
    list_filter = ["is_staff", "is_active", "is_email_verified"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "phone_number", "mpesa_phone")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser",
                                    "is_email_verified", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "first_name", "last_name", "password1", "password2")}),
    )
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "created_at"]


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "is_used", "created_at"]
