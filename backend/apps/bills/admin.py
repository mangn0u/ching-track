from django.contrib import admin

from .models import Bill, BillPayment


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "amount", "currency_code", "due_day", "frequency", "is_active"]
    list_filter = ["frequency", "is_active"]
    search_fields = ["name", "user__email"]


@admin.register(BillPayment)
class BillPaymentAdmin(admin.ModelAdmin):
    list_display = ["bill", "paid_date", "amount_paid"]
    date_hierarchy = "paid_date"
