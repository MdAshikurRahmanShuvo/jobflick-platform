from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="user-dashboard"),
    path("edit/", views.edit_profile_view, name="userprofile-edit"),
    path("chat/", views.chat_view, name="userprofile-chat"),
    path("activity/", views.activity_view, name="userprofile-activity"),
    path("help/", views.help_view, name="userprofile-help"),
    path("about/", views.dashboard_about_view, name="userprofile-about"),
    path("contact/", views.dashboard_contact_view, name="userprofile-contact"),
]
