"""Analytics URL patterns."""

from django.urls import path
from apps.analytics.views import DashboardView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
