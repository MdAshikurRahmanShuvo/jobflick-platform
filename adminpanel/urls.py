from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="adminpanel-login"),
    path("logout/", views.logout_view, name="adminpanel-logout"),
    path("", views.dashboard_view, name="adminpanel-dashboard"),
    path("users/<int:user_id>/delete/", views.delete_user, name="adminpanel-delete-user"),
    path("jobs/<int:job_id>/delete/", views.delete_job, name="adminpanel-delete-job"),
    path("jobs/<int:job_id>/status/", views.handle_job_post_status, name="adminpanel-job-status"),
    path("applications/<int:pk>/status/", views.handle_application_status, name="adminpanel-application-status"),
    path("transactions/create/", views.create_transaction, name="adminpanel-create-transaction"),
    path("transactions/<int:pk>/mark-paid/", views.mark_transaction_paid, name="adminpanel-mark-transaction-paid"),
    path(
        "notifications/<int:pk>/delete/",
        views.delete_notification,
        name="adminpanel-delete-notification",
    ),
]
