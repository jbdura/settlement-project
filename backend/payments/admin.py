# payments/admin.py

from django.contrib import admin
from .models import Merchant, Payment, Fee, Settlement


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "settlement_account",
        "created_at",
    )
    search_fields = ("name", "settlement_account")
    ordering = ("name",)
    readonly_fields = ("id", "created_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "merchant",
        "amount",
        "method",
        "status",
        "created_at",
    )
    list_filter = (
        "method",
        "status",
        "created_at",
    )
    search_fields = (
        "id",
        "merchant__name",
    )
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")
    autocomplete_fields = ("merchant",)

    fieldsets = (
        ("Payment Info", {
            "fields": ("merchant", "amount", "method", "status")
        }),
        ("Metadata", {
            "fields": ("id", "created_at"),
        }),
    )


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = (
        "method",
        "percentage",
    )
    ordering = ("method",)
    readonly_fields = ()

    # Prevent accidental deletes of fee configuration (optional but wise)
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "merchant",
        "gross_amount",
        "fee_amount",
        "net_amount",
        "created_at",
    )
    list_filter = (
        "created_at",
        "merchant",
    )
    search_fields = (
        "id",
        "merchant__name",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "merchant",
        "gross_amount",
        "fee_amount",
        "net_amount",
        "created_at",
    )
