from urllib.parse import urlencode
from typing import Optional

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, views as auth_views
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .forms import SignupForm
from userprofile.models import UserProfile

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
        UserProfile.objects.create(user=user)

        login(request, user)
        messages.success(request, "Signup successful!")
        return redirect("home")

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
            messages.error(request, "Invalid username or password!")

    return render(request, 'accounts/login.html')


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
