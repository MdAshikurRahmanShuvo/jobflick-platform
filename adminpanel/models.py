from django.conf import settings
from django.db import models


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

# Create your models here.
