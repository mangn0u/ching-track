"""M-Pesa URL patterns."""

from django.urls import path
from apps.transactions.mpesa_views import ParseSmsView, ConfirmImportView

urlpatterns = [
    path("parse-sms/", ParseSmsView.as_view(), name="mpesa-parse-sms"),
    path("confirm-import/", ConfirmImportView.as_view(), name="mpesa-confirm-import"),
]
