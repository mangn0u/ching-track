"""Development settings — DEBUG on, console email, verbose errors."""

from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all in dev
ALLOWED_HOSTS = ["*"]

# Print emails to terminal instead of sending
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# LocMemCache works fine for single-process dev (rate limits aren't shared
# across workers, but there are no workers locally — so it doesn't matter).
# Silence the django-ratelimit system check that would otherwise block startup.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Silence django-ratelimit's E003 error in dev.
# In production, replace the cache with Redis to remove this suppression.
SILENCED_SYSTEM_CHECKS = ["django_ratelimit.E003"]

# Django Debug Toolbar (optional — install separately)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# INTERNAL_IPS = ["127.0.0.1"]
