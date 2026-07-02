"""Analytics URL patterns."""

from django.urls import path
from apps.analytics.views import DashboardView, TrendsView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("trends/", TrendsView.as_view(), name="trends"),
]
