import dj_database_url
import urllib.parse
import secrets
import sys
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, EmailStr, Field

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-v-%xb5aw2jed2xw#-@2a5d55u5n!s2^km0pqij-6@a)8)$@#np"
DEBUG = True
ALLOWED_HOSTS = []
ENV_FILE = os.environ.get(
    "HBD_ENV_FILE", "test.env" if "pytest" in sys.modules else ".env"
)


class Settings(BaseSettings):
    """
    Pydantic-powered settings, to provide consistent error messages, strong
    typing, consistent prefixes, .venv support, etc.
    """

    #: The default database.
    DATABASE_SERVER: AnyUrl | None = None

    #: Should django run in debug mode?
    DEBUG: bool = False

    #: Should the debug toolbar be loaded?
    DEBUG_TOOLBAR: bool = False

    #: Set a secret key used for signing values such as sessions. Randomized
    #: by default, so you'll logout everytime the process restarts.
    SECRET_KEY: str = Field(default_factory=lambda: "autokey-" + secrets.token_hex(128))

    EMAIL_SERVER: AnyUrl = AnyUrl("console://localhost")
    EMAIL_FROM: EmailStr = "test@example.com"
    ERROR_EMAILS: list[EmailStr] | None = None

    PGHOST: str | None = Field(None, alias="PGHOST")
    PGPORT: int | None = Field(5432, alias="PGPORT")
    PGNAME: str = Field("herebedragons", alias="PGNAME")
    PGUSER: str = Field("postgres", alias="PGUSER")
    PGPASSWORD: str | None = Field(None, alias="PGPASSWORD")

    model_config = {
        "env_prefix": "HBD_",
        "env_file": str(BASE_DIR / ENV_FILE),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @staticmethod
    def as_bool(v: str | list[str] | None):
        if v is None:
            return False

        if isinstance(v, str):
            v = [v]

        return v[0].lower() in ("true", "yes", "t", "1")


SETUP = Settings()

# Don't allow automatic keys in production
if not SETUP.DEBUG and SETUP.SECRET_KEY.startswith("autokey-"):
    print("You must set HBD_SECRET_KEY in production")
    sys.exit(1)
SECRET_KEY = SETUP.SECRET_KEY
DEBUG = SETUP.DEBUG

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "tracking",
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
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "herebedragons.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "herebedragons.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if SETUP.DATABASE_SERVER:
    DATABASES = {
        "default": dj_database_url.parse(str(SETUP.DATABASE_SERVER), conn_max_age=600)
    }
    DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "HOST": SETUP.PGHOST,
            "PORT": SETUP.PGPORT,
            "NAME": SETUP.PGNAME,
            "USER": SETUP.PGUSER,
            "PASSWORD": SETUP.PGPASSWORD,
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static-collected"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
WHITENOISE_MAX_AGE = 3600

# Debug toolbar should only be loaded at all when debug is on
if DEBUG and SETUP.DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": "core.middleware.show_toolbar"}
    MIDDLEWARE.insert(8, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Email settings
SERVER_EMAIL = SETUP.EMAIL_FROM
if SETUP.EMAIL_SERVER:
    parsed = urllib.parse.urlparse(str(SETUP.EMAIL_SERVER))
    query = urllib.parse.parse_qs(parsed.query)
    if parsed.scheme == "console":
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    elif parsed.scheme == "sendgrid":
        EMAIL_HOST = "smtp.sendgrid.net"
        EMAIL_PORT = 587
        EMAIL_HOST_USER = "apikey"
        # urlparse will lowercase it
        EMAIL_HOST_PASSWORD = str(SETUP.EMAIL_SERVER).split("://")[1]
        EMAIL_USE_TLS = True
    elif parsed.scheme == "smtp":
        EMAIL_HOST = parsed.hostname
        EMAIL_PORT = parsed.port
        if parsed.username is not None:
            EMAIL_HOST_USER = urllib.parse.unquote(parsed.username)
        if parsed.password is not None:
            EMAIL_HOST_PASSWORD = urllib.parse.unquote(parsed.password)
        EMAIL_USE_TLS = Settings.as_bool(query.get("tls"))
        EMAIL_USE_SSL = Settings.as_bool(query.get("ssl"))
    else:
        raise ValueError("Unknown schema for EMAIL_SERVER.")
