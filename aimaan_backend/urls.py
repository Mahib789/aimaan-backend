from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import include, path


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "home.html")


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


def health_check(request):
    return JsonResponse({"status": "ok", "project": "AIMaan Backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),

    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),

    # Web/API modules
    path("predict/", include("ml_engine.urls")),
    path("ocr/", include("ocr_engine.urls")),
    path("learning/", include("learning.urls")),
    path("quiz/", include("quiz.urls")),
    path("accounts/", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)