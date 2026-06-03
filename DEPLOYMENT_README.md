# AIMaan Deployment-Ready Backend

This corrected version is prepared for Django deployment and Flutter integration.

## What was fixed

- Removed hardcoded production secret usage from settings.
- `DEBUG` now comes from environment variables.
- Added PostgreSQL support through `DATABASE_URL`.
- Added WhiteNoise static-file serving.
- Added `STATIC_ROOT` for `collectstatic`.
- Converted `requirements.txt` to normal UTF-8.
- Added token-based API auth for Flutter.
- Added mobile-friendly JSON/multipart prediction APIs.
- Removed Windows-only hardcoded Tesseract path; now uses `TESSERACT_CMD` env var.
- Added upload-size validation for OCR.
- Added `/health/` endpoint.
- Added `.env.example`, `.gitignore`, `Procfile`, and `build.sh`.
- Removed `db.sqlite3`, `feedback.csv`, `media`, `staticfiles`, and Python cache files from the deployment package.

## Local run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

For Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Important environment variables for hosting

```env
DJANGO_SECRET_KEY=your-strong-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.onrender.com,your-domain.com
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
CORS_ALLOWED_ORIGINS=https://your-frontend.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
TESSERACT_CMD=/usr/bin/tesseract
```

## Render build settings

Build command:

```bash
./build.sh
```

Start command:

```bash
gunicorn aimaan_backend.wsgi:application
```

## Database recommendation

Use PostgreSQL for deployment. SQLite is okay only for local testing.

## Flutter connection

See `FLUTTER_API_GUIDE.md` for endpoints and request examples.
