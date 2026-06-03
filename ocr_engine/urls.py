from django.urls import path
from .views import ocr_predict

urlpatterns = [
    path('', ocr_predict),   # IMPORTANT
]