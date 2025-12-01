"""Utility helpers for user profile workflows."""

from django.contrib.auth import get_user_model

from .models import Notification


def notify_staff(message: str, link: str = "") -> None:
    """Send a notification to every active staff account."""
    staff_ids = list(
        get_user_model()
        .objects.filter(is_staff=True, is_active=True)
        .values_list("id", flat=True)
    )
    if not staff_ids:
        return
    Notification.objects.bulk_create(
        [
            Notification(
                user_id=user_id,
                message=message,
                link=link,
                is_staff_only=True,
            )
            for user_id in staff_ids
        ]
    )
