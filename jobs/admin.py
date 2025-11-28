from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
	list_display = ("work_title", "worker_type", "location", "amount", "created_at")
	search_fields = ("work_title", "worker_type", "location", "skills")
	list_filter = ("worker_type", "location", "created_at")
