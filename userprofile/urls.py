from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="user-dashboard"),
    path("edit/", views.edit_profile_view, name="userprofile-edit"),
    path("subscription/", views.subscription_view, name="userprofile-subscription"),
    path(
        "subscription/status/",
        views.subscription_status_view,
        name="userprofile-subscription-status",
    ),
    path("chat/", views.chat_view, name="userprofile-chat"),
    path("activity/", views.activity_view, name="userprofile-activity"),
    path("transactions/", views.transactions_view, name="userprofile-transactions"),
    path("help/", views.help_view, name="userprofile-help"),
    path("about/", views.dashboard_about_view, name="userprofile-about"),
    path("contact/", views.dashboard_contact_view, name="userprofile-contact"),
    path("notifications/", views.notifications_view, name="userprofile-notifications"),
    path(
        "notifications/<int:pk>/",
        views.notification_detail_view,
        name="userprofile-notification-detail",
    ),
    path(
        "notifications/<int:pk>/delete/",
        views.delete_notification_view,
        name="userprofile-notification-delete",
    ),
]
