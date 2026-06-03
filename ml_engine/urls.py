from django.urls import path

from .views import (
    predict_text,
    submit_feedback,
    ocr_only
)

urlpatterns = [

    path(
        "",
        predict_text,
        name="predict"
    ),

    path(
        "feedback/",
        submit_feedback,
        name="feedback"
    ),

    path(
        "ocr/",
        ocr_only,
        name="ocr"
    ),
]