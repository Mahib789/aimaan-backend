from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path("api/signup/", api_views.api_signup, name="api_signup"),
    path("api/login/", api_views.api_login, name="api_login"),
    path("api/me/", api_views.api_me, name="api_me"),
    path("api/logout/", api_views.api_logout, name="api_logout"),

    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path(
        "forgot-password/",
        views.forgot_password_view,
        name="forgot_password"
    ),
]