from django.contrib import admin

from .models import SubscriptionLedgerEntry, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ("recipient", "job", "amount", "status", "created_at")
	list_filter = ("status", "created_at")
	search_fields = ("recipient__username", "recipient__email", "job__work_title")
	autocomplete_fields = ("recipient", "job")


@admin.register(SubscriptionLedgerEntry)
class SubscriptionLedgerEntryAdmin(admin.ModelAdmin):
	list_display = ("user", "plan", "amount", "created_at")
	list_filter = ("plan", "created_at")
	search_fields = ("user__username", "user__email")
