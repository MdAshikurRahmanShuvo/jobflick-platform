from django.conf import settings
from django.db import models

from userprofile.models import UserProfile


class Transaction(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		PAID = "paid", "Paid"

	recipient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="payout_transactions",
	)
	job = models.ForeignKey(
		"jobs.Job",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="transactions",
	)
	amount = models.PositiveIntegerField()
	note = models.CharField(max_length=255, blank=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	processed_at = models.DateTimeField(blank=True, null=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.recipient} - {self.amount}"


class SubscriptionLedgerEntry(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="subscription_ledger_entries",
	)
	plan = models.CharField(max_length=20, choices=UserProfile.SubscriptionPlan.choices)
	amount = models.PositiveIntegerField()
	wallet_before = models.PositiveIntegerField()
	wallet_after = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user} - {self.amount} BDT ({self.get_plan_display()})"

# Create your models here.
