import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me-before-production")
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes", "on")

render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME", "")
allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "")

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "10.1.3.22",
]

if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)

if allowed_hosts_env:
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in allowed_hosts_env.split(",")
        if host.strip()
    )

CSRF_TRUSTED_ORIGINS = []
if render_hostname:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "leaveapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Sprint 4 展示版先使用 SQLite。
# Render 免費 Web Service 的本機檔案系統不是永久儲存；
# 正式上線時應改用 PostgreSQL。
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "zh-hant"
TIME_ZONE = "Asia/Taipei"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Render's normal filesystem is ephemeral. When CLOUDINARY_URL is configured,
# user-uploaded leave attachments are stored persistently on Cloudinary.
# Local development keeps using the normal media/ folder when the variable is
# absent, so no Cloudinary account is required just to run the project locally.
DEFAULT_MEDIA_STORAGE = (
    "leaveapp.storage.CloudinaryRawStorage"
    if os.getenv("CLOUDINARY_URL")
    else "django.core.files.storage.FileSystemStorage"
)

STORAGES = {
    "default": {
        "BACKEND": DEFAULT_MEDIA_STORAGE,
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = False
