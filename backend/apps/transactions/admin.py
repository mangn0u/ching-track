from django.contrib import admin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "user", "is_default", "color"]
    list_filter = ["type", "is_default"]
    search_fields = ["name", "user__email"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "amount", "currency_code", "category", "date", "is_deleted"]
    list_filter = ["type", "currency_code", "is_deleted"]
    search_fields = ["user__email", "note", "mpesa_ref"]
    date_hierarchy = "date"
