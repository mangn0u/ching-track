"""Custom middleware — security headers and request processing."""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class CSPMiddleware(MiddlewareMixin):
    """
    Sets Content-Security-Policy headers on every response.
    Only active when SECURE_CSP is configured in settings.
    """

    CSP_DIRECTIVES = {
        "default-src": getattr(settings, "CSP_DEFAULT_SRC", ("'self'",)),
        "style-src": getattr(settings, "CSP_STYLE_SRC", ("'self'", "'unsafe-inline'")),
        "script-src": getattr(settings, "CSP_SCRIPT_SRC", ("'self'",)),
        "img-src": getattr(settings, "CSP_IMG_SRC", ("'self'", "data:")),
        "font-src": getattr(settings, "CSP_FONT_SRC", ("'self'",)),
        "connect-src": getattr(settings, "CSP_CONNECT_SRC", ("'self'",)),
        "frame-ancestors": getattr(settings, "CSP_FRAME_ANCESTORS", ("'none'",)),
        "base-uri": getattr(settings, "CSP_BASE_URI", ("'self'",)),
        "form-action": getattr(settings, "CSP_FORM_ACTION", ("'self'",)),
    }

    def process_response(self, request, response):
        header_value = "; ".join(
            f"{directive} {' '.join(sources)}"
            for directive, sources in self.CSP_DIRECTIVES.items()
            if sources
        )
        if header_value:
            response["Content-Security-Policy"] = header_value
        return response
