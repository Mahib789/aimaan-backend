import json
import os
import re

import cv2
import numpy as np
import pytesseract
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import PredictionFeedback
from .service import predict_message


if getattr(settings, "TESSERACT_CMD", ""):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


MAX_UPLOAD_MB = int(os.environ.get("MAX_OCR_UPLOAD_MB", "5"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def clean_ocr_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_image(image_file):
    if image_file.size and image_file.size > MAX_UPLOAD_BYTES:
        raise ValueError(f"Image too large. Maximum allowed size is {MAX_UPLOAD_MB} MB.")

    file_bytes = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image file. Please upload a clear JPG or PNG image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    raw_text = pytesseract.image_to_string(gray, config="--psm 6")
    return clean_ocr_text(raw_text)


@api_view(["GET", "POST"])
@parser_classes([JSONParser, MultiPartParser, FormParser])
@permission_classes([AllowAny])
def predict_text(request):
    """
    Flutter/web endpoint.
    Text request JSON: {"text": "your message"}
    Image request multipart: image=<file>
    Optional auth header: Authorization: Token <token>
    """
    if request.method == "GET":
        return Response({
            "message": "AIMaan prediction API is running.",
            "text_example": {"text": "Your OTP is 123456"},
            "image_field": "image",
        })

    try:
        image = request.FILES.get("image")
        if image:
            extracted_text = extract_text_from_image(image)
            if not extracted_text:
                return Response(
                    {"error": "No readable text found in image. Please upload a clear screenshot."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = predict_message(extracted_text)
            result.update({
                "source": "image",
                "extracted_text": extracted_text,
                "message_text": extracted_text,
            })
            return Response(result)

        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"error": "Text required."}, status=status.HTTP_400_BAD_REQUEST)

        result = predict_message(text)
        result.update({"source": "text", "message_text": text})
        return Response(result)

    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@parser_classes([JSONParser, MultiPartParser, FormParser])
@permission_classes([AllowAny])
def submit_feedback(request):
    try:
        PredictionFeedback.objects.create(
            user=request.user if request.user and request.user.is_authenticated else None,
            text=request.data.get("text", ""),
            predicted_label=request.data.get("label", ""),
            safe_prob=float(request.data.get("safe", 0)),
            fraud_prob=float(request.data.get("fraud", 0)),
            user_feedback=request.data.get("feedback", "correct"),
            comment=request.data.get("comment", ""),
            source=request.data.get("source", "text"),
        )
        return Response({"message": "Feedback saved."}, status=status.HTTP_201_CREATED)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def ocr_only(request):
    image = request.FILES.get("image")
    if not image:
        return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        text = extract_text_from_image(image)
        if not text:
            return Response(
                {"error": "No readable text found in image. Please upload a clear screenshot."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"extracted_text": text, "source": "ocr"})
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
