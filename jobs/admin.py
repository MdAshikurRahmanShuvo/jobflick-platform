from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
	list_display = ("work_title", "worker_type", "location", "amount", "created_at")
	search_fields = ("work_title", "worker_type", "location", "skills")
	list_filter = ("worker_type", "location", "created_at")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
	list_display = ("job", "applicant", "status", "created_at", "decision_at")
	list_filter = ("status", "created_at")
	search_fields = ("job__work_title", "applicant__username", "job__tracking_code")
	autocomplete_fields = ("job", "applicant", "decided_by")
