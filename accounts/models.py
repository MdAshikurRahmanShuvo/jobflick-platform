from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class EmailOTP(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="email_otp")
	code = models.CharField(max_length=6)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	verified = models.BooleanField(default=False)

	OTP_LIFETIME = timedelta(minutes=10)

	def __str__(self):
		return f"OTP for {self.user.username}"

	def is_expired(self):
		return timezone.now() > (self.updated_at + self.OTP_LIFETIME)
