import random
from datetime import timedelta
from urllib.parse import urlencode
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, views as auth_views
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import SignupForm
from .models import EmailOTP
from userprofile.models import UserProfile

OTP_EXPIRY = timedelta(minutes=10)


def _generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"


def _send_verification_email(user: User, code: str) -> None:
    subject = "Verify your JobFlick account"
    message = (
        f"Hi {user.username},\n\n"
        f"Your verification code is {code}. It expires in {int(OTP_EXPIRY.total_seconds() // 60)} minutes.\n\n"
        "If you did not request this code, you can ignore this email.\n\n"
        "— JobFlick"
    )
    sender = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@jobflick.com")
    send_mail(subject, message, sender, [user.email], fail_silently=False)


def _create_or_refresh_otp(user: User) -> EmailOTP:
    code = _generate_otp()
    otp_obj, _ = EmailOTP.objects.update_or_create(
        user=user,
        defaults={"code": code, "verified": False},
    )
    _send_verification_email(user, code)
    return otp_obj


def _pending_user_id(request) -> Optional[int]:
    return request.session.get("pending_email_user_id")


def _set_pending_user(request, user: User) -> None:
    request.session["pending_email_user_id"] = user.id


def _clear_pending_user(request) -> None:
    request.session.pop("pending_email_user_id", None)

# ---------- SIGNUP ----------
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        # Duplicate username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken! Try another one.")
            return redirect("signup")

        # Duplicate email check
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered!")
            return redirect("signup")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_active = False
        user.save(update_fields=["is_active"])
        UserProfile.objects.create(user=user)

        _create_or_refresh_otp(user)
        _set_pending_user(request, user)
        messages.success(request, "Signup successful! We emailed you a verification code.")
        return redirect("verify-otp")

    return render(request, "accounts/signup.html")



# ---------- LOGIN ----------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('user-dashboard')
        else:
            pending_user = User.objects.filter(username=username).first()
            if pending_user and pending_user.check_password(password) and not pending_user.is_active:
                _set_pending_user(request, pending_user)
                _create_or_refresh_otp(pending_user)
                messages.warning(request, "Please verify the code we sent to your email before logging in.")
                return redirect('verify-otp')

            messages.error(request, "Invalid username or password!")

    return render(request, 'accounts/login.html')


def verify_otp_view(request):
    pending_id = _pending_user_id(request)

    if not pending_id and request.user.is_authenticated and request.user.is_active:
        return redirect('user-dashboard')

    user = User.objects.filter(id=pending_id).first() if pending_id else None
    if not user:
        messages.info(request, "Please create an account first.")
        return redirect('signup')

    otp_obj = EmailOTP.objects.filter(user=user).first()
    if otp_obj is None:
        otp_obj = _create_or_refresh_otp(user)

    if request.method == "POST":
        submitted_code = request.POST.get("otp", "").strip()

        if not submitted_code:
            messages.error(request, "Enter the 6-digit code from your email.")
        elif otp_obj.is_expired():
            _create_or_refresh_otp(user)
            messages.warning(request, "The code expired. We sent a new one.")
            return redirect('verify-otp')
        elif submitted_code != otp_obj.code:
            messages.error(request, "The code you entered is incorrect.")
        else:
            otp_obj.verified = True
            otp_obj.save(update_fields=["verified"])
            user.is_active = True
            user.save(update_fields=["is_active"])
            _clear_pending_user(request)
            messages.success(request, "Email verified! Please log in to continue.")
            return redirect('login')

    context = {
        "email": user.email,
    }
    return render(request, "accounts/verify_otp.html", context)


def resend_otp_view(request):
    if request.method != "POST":
        return redirect('verify-otp')

    pending_id = _pending_user_id(request)
    user = User.objects.filter(id=pending_id).first() if pending_id else None
    if not user:
        messages.error(request, "We could not find a pending verification. Please sign up again.")
        return redirect('signup')

    _create_or_refresh_otp(user)
    messages.success(request, "We sent a new verification code to your email.")
    return redirect('verify-otp')


# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')


def _append_next_query(url: str, next_value: Optional[str]) -> str:
    """Return URL with ?next=<value> appended when provided."""
    if not next_value:
        return url
    separator = '&' if '?' in url else '?'
    return f"{url}{separator}{urlencode({'next': next_value})}"


class NextAwarePasswordResetView(auth_views.PasswordResetView):
    """Password reset view that keeps track of the desired login redirect."""

    email_template_name = "accounts/password_reset_email.html"

    def dispatch(self, request, *args, **kwargs):
        self.next_target = request.GET.get("next")
        if self.next_target:
            base_context = self.extra_email_context.copy() if self.extra_email_context else {}
            base_context["next"] = self.next_target
            self.extra_email_context = base_context
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = getattr(self, "next_target", None)
        return context

    def get_success_url(self):
        url = super().get_success_url()
        return _append_next_query(url, getattr(self, "next_target", None))


class NextAwarePasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """Password reset confirm view that forwards ?next to the completion page."""

    def dispatch(self, request, *args, **kwargs):
        self.next_target = request.GET.get("next")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = getattr(self, "next_target", None)
        return context

    def get_success_url(self):
        url = super().get_success_url()
        return _append_next_query(url, getattr(self, "next_target", None))
