"""Accounts URL patterns."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

# TODO Day 2: import views and wire up routes
# from .views import (
#     RegisterView, VerifyEmailView, LoginView, LogoutView,
#     MeView, ChangePasswordView, ForgotPasswordView,
#     ResetPasswordView, ExportDataView, DeleteAccountView,
# )

urlpatterns = [
    # path("register/", RegisterView.as_view(), name="auth-register"),
    # path("verify-email/<uuid:token>/", VerifyEmailView.as_view(), name="auth-verify-email"),
    # path("login/", LoginView.as_view(), name="auth-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    # path("logout/", LogoutView.as_view(), name="auth-logout"),
    # path("me/", MeView.as_view(), name="auth-me"),
    # path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    # path("forgot-password/", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    # path("reset-password/<uuid:token>/", ResetPasswordView.as_view(), name="auth-reset-password"),
    # path("export-data/", ExportDataView.as_view(), name="auth-export-data"),
    # path("delete-account/", DeleteAccountView.as_view(), name="auth-delete-account"),
]
