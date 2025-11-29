from django.contrib import admin
from .models import Notification, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "display_name")
	search_fields = ("user__username", "display_name")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user", "message", "is_read", "created_at")
	list_filter = ("is_read", "created_at")
	search_fields = ("user__username", "message")
