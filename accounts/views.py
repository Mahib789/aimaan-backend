from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .validators import strong_password_validator


# -------------------
# SIGNUP VIEW
# -------------------
def signup_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        full_name = request.POST.get("full_name", "")

        password1 = request.POST.get("password1") or request.POST.get("password")
        password2 = request.POST.get("password2") or password1

        if not username or not email or not password1:
            return render(request, "signup.html", {
                "error": "All fields are required."
            })

        if password1 != password2:
            return render(request, "signup.html", {
                "error": "Passwords do not match."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "Username already exists."
            })

        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {
                "error": "Email already exists."
            })

        try:
            strong_password_validator(password1)
        except ValidationError as e:
            return render(request, "signup.html", {
                "error": e.message
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.first_name = full_name
        user.save()

        return redirect("login")

    return render(request, "signup.html")


# -------------------
# LOGIN VIEW
# -------------------
def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(request, "login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "login.html")


# -------------------
# FORGOT PASSWORD VIEW
# -------------------
def forgot_password_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not username or not email or not password1 or not password2:
            return render(request, "forgot_password.html", {
                "error": "All fields are required."
            })

        if password1 != password2:
            return render(request, "forgot_password.html", {
                "error": "Passwords do not match."
            })

        try:
            strong_password_validator(password1)
        except ValidationError as e:
            return render(request, "forgot_password.html", {
                "error": e.message
            })

        try:
            user = User.objects.get(
                username=username,
                email=email
            )
        except User.DoesNotExist:
            return render(request, "forgot_password.html", {
                "error": "No account found with this username and email."
            })

        user.set_password(password1)
        user.save()

        return render(request, "forgot_password.html", {
            "success": "✅ Password reset successfully! Redirecting to login..."
        })

    return render(request, "forgot_password.html")


# -------------------
# LOGOUT VIEW
# -------------------
def logout_view(request):
    logout(request)
    return redirect("login")


# -------------------
# DASHBOARD VIEW
# -------------------
@login_required(login_url="login")
def dashboard(request):
    return render(request, "dashboard.html")