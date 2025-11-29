from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
	display_name = models.CharField(max_length=150, blank=True)
	photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
	occupation = models.CharField(max_length=150, blank=True)
	skills = models.TextField(blank=True)
	present_address = models.CharField(max_length=255, blank=True)
	bio = models.TextField(blank=True)

	def __str__(self):
		if self.display_name:
			return self.display_name
		return self.user.get_username()


class Notification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
	message = models.TextField()
	link = models.CharField(max_length=255, blank=True)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Notification for {self.user}" 
