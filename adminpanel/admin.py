from django.contrib import admin

from .models import SubscriptionLedgerEntry


@admin.register(SubscriptionLedgerEntry)
class SubscriptionLedgerEntryAdmin(admin.ModelAdmin):
	list_display = ("user", "plan", "amount", "created_at")
	list_filter = ("plan", "created_at")
	search_fields = ("user__username", "user__email")
