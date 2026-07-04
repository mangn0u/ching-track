"""Development settings — DEBUG on, console email, verbose errors."""

from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all in dev
ALLOWED_HOSTS = ["*"]

# Print emails to terminal instead of sending
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Rate limiting cache (locmem is fine for single-process dev)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Django Debug Toolbar (optional — install separately)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# INTERNAL_IPS = ["127.0.0.1"]
