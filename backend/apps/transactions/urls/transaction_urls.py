"""Transaction URL patterns."""

from django.urls import path
from apps.transactions.views import (
    TransactionListCreateView,
    TransactionDetailView,
    TransactionSummaryView,
)

urlpatterns = [
    path("", TransactionListCreateView.as_view(), name="transaction-list"),
    path("summary/", TransactionSummaryView.as_view(), name="transaction-summary"),
    path("<int:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
]
