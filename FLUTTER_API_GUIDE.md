# AIMaan Flutter API Guide

Base URL examples:
- Local: `http://10.0.2.2:8000` for Android emulator
- Physical phone on same Wi-Fi: `http://YOUR_PC_IP:8000`
- Hosted: `https://your-backend.onrender.com`

## Auth

### Signup
`POST /accounts/api/signup/`
```json
{
  "username": "mahib",
  "email": "mahib@example.com",
  "full_name": "Mahib Hussain",
  "password": "StrongPass123!",
  "password2": "StrongPass123!"
}
```

### Login
`POST /accounts/api/login/`
```json
{
  "username": "mahib",
  "password": "StrongPass123!"
}
```

Response:
```json
{
  "token": "abc123...",
  "user": {"id": 1, "username": "mahib", "email": "mahib@example.com"}
}
```

Use this header for protected endpoints:
`Authorization: Token YOUR_TOKEN`

## Text prediction
`POST /predict/`
```json
{
  "text": "Your HBL account is blocked verify OTP now"
}
```

## Image OCR + prediction
`POST /predict/` multipart/form-data with field name `image`.

## OCR only
`POST /predict/ocr/` multipart/form-data with field name `image`.

## Feedback
`POST /predict/feedback/`
```json
{
  "text": "Your HBL account is blocked verify OTP now",
  "label": "FRAUD",
  "safe": 0.01,
  "fraud": 0.99,
  "feedback": "correct",
  "comment": "Good result",
  "source": "text"
}
```
