from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core env ---
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DEBUG", "0") == "1"

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

# --- Application definition ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",

    # local apps (если у тебя другие названия — поправь)
    "users",
    "habits",
    "telegram_bot",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database (PostgreSQL in Docker) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "habits"),
        "USER": os.getenv("POSTGRES_USER", "habits"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "habits"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n / tz ---
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Moscow")
USE_I18N = True
USE_TZ = True

# --- Static / Media (for nginx) ---
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = "/static"
MEDIA_ROOT = "/media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Custom user model ---
AUTH_USER_MODEL = "users.User"

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,  # пагинация по ТЗ
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# --- OpenAPI / Swagger ---
SPECTACULAR_SETTINGS = {
    "TITLE": "Habits API",
    "DESCRIPTION": "Сервис трекинга привычек с напоминаниями в Telegram",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# --- CORS ---
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_origins.split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS = True

# --- Celery ---
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# --- Celery Beat ---
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "send-habit-reminders-every-minute": {
        "task": "habits.tasks.send_habit_reminders",
        "schedule": crontab(minute="*"),
    },
}

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")