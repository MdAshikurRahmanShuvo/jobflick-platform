from django.conf import settings
from django.db import models

from userprofile.models import UserProfile


class SubscriptionLedgerEntry(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="subscription_ledger_entries",
	)
	plan = models.CharField(max_length=20, choices=UserProfile.SubscriptionPlan.choices)
	amount = models.PositiveIntegerField()
	wallet_before = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user} - {self.amount} BDT ({self.get_plan_display()})"

# Create your models here.
