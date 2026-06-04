import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-demo-only")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "webhooks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DATABASE_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}

USE_TZ = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STRIPE_WEBHOOK_SECRET = os.environ.get(
    "STRIPE_WEBHOOK_SECRET",
    "whsec_synthetic_demo_secret",
)
MOLLIE_WEBHOOK_SECRET = os.environ.get(
    "MOLLIE_WEBHOOK_SECRET", "mollie_synthetic_demo_secret"
)
