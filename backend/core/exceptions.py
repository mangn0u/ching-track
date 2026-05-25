"""Custom exception handler — consistent JSON error format."""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to produce a consistent shape:

    {
        "error": true,
        "message": "A human-readable summary",
        "details": { ...field-level errors... }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        original_data = response.data

        response.data = {
            "error": True,
            "message": _extract_message(original_data),
            "details": original_data,
        }

    return response


def _extract_message(data):
    """Pull a top-level summary string from DRF error data."""
    if isinstance(data, list) and data:
        return str(data[0])
    if isinstance(data, dict):
        for key in ("detail", "non_field_errors"):
            if key in data:
                val = data[key]
                return str(val[0]) if isinstance(val, list) else str(val)
        first_key = next(iter(data))
        val = data[first_key]
        return str(val[0]) if isinstance(val, list) else str(val)
    return "An error occurred."
