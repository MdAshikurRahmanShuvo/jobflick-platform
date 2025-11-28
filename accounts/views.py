from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignupForm

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
    return redirect('login')
