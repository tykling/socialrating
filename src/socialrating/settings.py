"""
Django settings for socialrating project.
"""
import os
from .environment_settings import *  # noqa: F401 F403

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # needed for allauth
    "django.contrib.humanize",  # stuff like "timesince" template filter
    "django.contrib.gis",  # geodjango
    "leaflet",  # pretty maps
    "guardian",  # object level permissions
    "eav",  # forked django-eav2 used for all the dynamic data storage
    "bootstrap4",  # for templates of niceness
    "taggit",  # tags for stuff
    # auth apps
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.windowslive",
    # socialraitng models
    "actor",
    "team",
    "category",
    "context",
    "fact",
    "item",
    "review",
    "rating",
    "vote",
    "utils",
    "forum",
    "thread",
    # gfk models
    "event",
    "attachment",
    "comment",
    # temp
    "cuptest",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "crum.CurrentRequestUserMiddleware",
]

ROOT_URLCONF = "socialrating.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "socialrating.wsgi.application"
ASGI_APPLICATION = "socialrating.routing.application"

AUTH_USER_MODEL = "actor.User"
LOGIN_REDIRECT_URL = "/"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
)
# ANONYMOUS_USER_NAME = "AnonymousUser"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_L10N = True
USE_TZ = True

# static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static_src")]  # find static files here
STATIC_ROOT = os.path.join(BASE_DIR, "static")  # collect static files here
STATIC_URL = "/static/"  # serve static files here
MEDIA_ROOT = "media/"  # keep uploads here

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "syslog": {"format": "%(levelname)s %(name)s.%(funcName)s(): %(message)s"},
        "console": {
            "format": "[%(asctime)s] %(name)s.%(funcName)s() %(levelname)s %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "console"}},
    "loggers": {"socialrating": {"handlers": ["console"], "level": "DEBUG"}},
}

DATABASE_ROUTERS = ["cuptest.routers.CupRouter"]
