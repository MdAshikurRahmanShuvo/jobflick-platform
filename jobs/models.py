from django.conf import settings
from django.db import models


class Job(models.Model):
	poster = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="jobs",
	)
	work_title = models.CharField(max_length=200)
	worker_type = models.CharField(max_length=120)
	duration = models.CharField(max_length=120)
	amount = models.PositiveIntegerField()
	location = models.CharField(max_length=120)
	skills = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.work_title
