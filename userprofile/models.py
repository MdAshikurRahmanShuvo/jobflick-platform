from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
	class SubscriptionPlan(models.TextChoices):
		NONE = "none", "No Subscription"
		ONE_MONTH = "one_month", "1 Month"
		SIX_MONTHS = "six_months", "6 Months"
		ONE_YEAR = "one_year", "12 Months"

	SUBSCRIPTION_DETAILS = {
		SubscriptionPlan.ONE_MONTH: {
			"price": 120,
			"duration_days": 30,
			"label": "1 Month Access",
			"description": "Quick access for trying Jobflick for a month.",
		},
		SubscriptionPlan.SIX_MONTHS: {
			"price": 500,
			"duration_days": 182,
			"label": "6 Months Access",
			"description": "Unlimited job posts and applications for half a year.",
		},
		SubscriptionPlan.ONE_YEAR: {
			"price": 800,
			"duration_days": 365,
			"label": "12 Months Access",
			"description": "Full-year access to post and apply without limits.",
		},
	}

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
	display_name = models.CharField(max_length=150, blank=True)
	photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
	occupation = models.CharField(max_length=150, blank=True)
	skills = models.TextField(blank=True)
	present_address = models.CharField(max_length=255, blank=True)
	bio = models.TextField(blank=True)
	wallet_balance = models.PositiveIntegerField(default=2000)
	subscription_plan = models.CharField(
		max_length=20,
		choices=SubscriptionPlan.choices,
		default=SubscriptionPlan.NONE,
	)
	subscription_expires_at = models.DateField(blank=True, null=True)

	def __str__(self):
		if self.display_name:
			return self.display_name
		return self.user.get_username()

	@property
	def has_active_subscription(self) -> bool:
		"""Return True when the subscription is current."""
		if not self.subscription_expires_at:
			return False
		return self.subscription_expires_at >= timezone.now().date()

	@property
	def subscription_days_left(self) -> int:
		"""Number of days remaining on the active subscription."""
		if not self.has_active_subscription:
			return 0
		return (self.subscription_expires_at - timezone.now().date()).days

	def apply_subscription(self, plan_key: str) -> None:
		"""Activate or extend a subscription for the provided plan."""
		plan = self.SUBSCRIPTION_DETAILS.get(plan_key)
		if not plan:
			raise ValueError("Unsupported subscription plan.")
		current_date = timezone.now().date()
		base_date = self.subscription_expires_at if self.has_active_subscription else current_date
		self.subscription_plan = plan_key
		self.subscription_expires_at = base_date + timedelta(days=plan["duration_days"])

	@classmethod
	def serialize_subscription_plans(cls):
		"""Return plan metadata ready for template consumption."""
		return [
			{"key": key, **details}
			for key, details in cls.SUBSCRIPTION_DETAILS.items()
		]


class Notification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
	message = models.TextField()
	link = models.CharField(max_length=255, blank=True)
	is_staff_only = models.BooleanField(default=False)
	subscription_entry = models.ForeignKey(
		"adminpanel.SubscriptionLedgerEntry",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="notifications",
	)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Notification for {self.user}" 
