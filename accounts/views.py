from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignupForm

# ---------- SIGNUP ----------
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # Check duplicate email
            if User.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered! Try another one.")
                return redirect("signup")

            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=email,
                password=form.cleaned_data["password"]
            )

            login(request, user)
            messages.success(request, "Signup successful!")
            return redirect('home')

    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


# ---------- LOGIN ----------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'accounts/login.html')


# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')
