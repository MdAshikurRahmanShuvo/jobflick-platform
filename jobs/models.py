from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


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
	tracking_code = models.CharField(max_length=16, unique=True, editable=False, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.work_title

	def save(self, *args, **kwargs):
		if not self.tracking_code:
			self.tracking_code = self._generate_tracking_code()
		super().save(*args, **kwargs)

	@staticmethod
	def _generate_tracking_code():
		"""Return a short unique tracking identifier like JB-0ABC12."""
		prefix = "JB"
		while True:
			candidate = f"{prefix}-{get_random_string(6).upper()}"
			if not Job.objects.filter(tracking_code=candidate).exists():
				return candidate


class JobApplication(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		APPROVED = "approved", "Approved"
		REJECTED = "rejected", "Rejected"

	job = models.ForeignKey(Job, related_name="applications", on_delete=models.CASCADE)
	applicant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="job_applications", on_delete=models.CASCADE)
	cover_letter = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	decided_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name="decided_applications",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	decision_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("job", "applicant")
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.applicant} -> {self.job}"

	def save(self, *args, **kwargs):
		previous_status = None
		if self.pk:
			previous_status = (
				JobApplication.objects.filter(pk=self.pk).values_list("status", flat=True).first()
			)
		super().save(*args, **kwargs)
		status_changed = previous_status != self.status
		if status_changed and self.status in {self.Status.APPROVED, self.Status.REJECTED}:
			self._notify_applicant()

	def _notify_applicant(self):
		Notification = apps.get_model("userprofile", "Notification")
		if self.status == self.Status.APPROVED:
			message = (
				f"Your application for '{self.job.work_title}' (Tracking {self.job.tracking_code}) has been approved."
			)
		else:
			message = (
				f"Your application for '{self.job.work_title}' (Tracking {self.job.tracking_code}) was declined."
			)
		Notification.objects.create(user=self.applicant, message=message)
