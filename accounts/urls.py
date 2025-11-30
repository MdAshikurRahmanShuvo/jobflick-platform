from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    NextAwarePasswordResetConfirmView,
    NextAwarePasswordResetView,
    login_view,
    logout_view,
    signup_view,
)

urlpatterns = [
    # Authentication
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Password Reset Request
    path(
        'password-reset/',
        NextAwarePasswordResetView.as_view(
            template_name="accounts/password_reset.html",
        ),
        name='password_reset'
    ),

    # Email Sent Page
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name='password_reset_done'
    ),

    # Link from Email - Form to Enter New Password
    path(
        'reset/<uidb64>/<token>/',
        NextAwarePasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url='/accounts/reset/done/'  # ✅ Correct success redirect
        ),
        name='password_reset_confirm'
    ),

    # Password Reset Complete
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name='password_reset_complete'
    ),
]
