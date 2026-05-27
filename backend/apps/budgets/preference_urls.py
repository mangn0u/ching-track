"""Preferences URL patterns."""

from django.urls import path
from apps.budgets.views import UserPreferencesView, SpendingStatusView

urlpatterns = [
    path("", UserPreferencesView.as_view(), name="preferences"),
    path("spending-status/", SpendingStatusView.as_view(), name="spending-status"),
]
