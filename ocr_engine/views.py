import os

import cv2
import numpy as np
import pytesseract
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


if getattr(settings, "TESSERACT_CMD", ""):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

MAX_UPLOAD_MB = int(os.environ.get("MAX_OCR_UPLOAD_MB", "5"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def extract_text(image_file):
    if image_file.size and image_file.size > MAX_UPLOAD_BYTES:
        raise ValueError(f"Image too large. Maximum allowed size is {MAX_UPLOAD_MB} MB.")

    file_bytes = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image file. Please upload JPG or PNG.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray).strip()


@api_view(["GET", "POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def ocr_predict(request):
    if request.method == "GET":
        return Response({"message": "POST an image using multipart field name 'image'."})

    image = request.FILES.get("image")
    if not image:
        return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        return Response({"extracted_text": extract_text(image)})
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
