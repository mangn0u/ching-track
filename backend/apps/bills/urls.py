"""Bills URL patterns."""

from django.urls import path
from apps.bills.views import BillListCreateView, BillDetailView, BillPayView, UpcomingBillsView

urlpatterns = [
    path("", BillListCreateView.as_view(), name="bill-list"),
    path("upcoming/", UpcomingBillsView.as_view(), name="bill-upcoming"),
    path("<int:pk>/", BillDetailView.as_view(), name="bill-detail"),
    path("<int:pk>/pay/", BillPayView.as_view(), name="bill-pay"),
]
