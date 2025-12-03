from django.contrib import admin

from .models import WalletTransaction


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "user",
        "direction",
        "category",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("direction", "category", "status")
    search_fields = ("reference", "user__username", "user__email")
    readonly_fields = ("reference", "created_at", "processed_at")
