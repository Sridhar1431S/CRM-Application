import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("crm_lite")


class BusinessRuleViolation(drf_exceptions.APIException):
    """
    Raised by the service layer when a domain/business rule is violated
    (e.g. moving a Won opportunity back to Qualification). Kept distinct
    from plain serializer ValidationError so services don't need to know
    about DRF field-level validation machinery.
    """

    status_code = 422
    default_detail = "The requested operation violates a business rule."
    default_code = "business_rule_violation"


def global_exception_handler(exc, context):
    """
    Central place that turns any exception raised inside a view into a
    consistent JSON error envelope:

        {
            "error": {
                "code": "validation_error",
                "message": "Human readable summary",
                "details": {...}   # optional, field-level errors
            }
        }

    DRF's default handler already deals with APIException subclasses
    (ValidationError, PermissionDenied, NotAuthenticated, NotFound, etc.).
    We normalize its output and add handling for a few Django-native
    exceptions that DRF does not translate automatically.
    """
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = drf_exceptions.PermissionDenied()
    elif isinstance(exc, DjangoValidationError):
        exc = drf_exceptions.ValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled exception -> log full traceback, return generic 500.
        logger.exception("Unhandled exception in view", exc_info=exc)
        return Response(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred. Please try again later.",
                }
            },
            status=500,
        )

    detail = response.data
    code = getattr(exc, "default_code", "error")

    if isinstance(detail, dict) and "detail" not in detail:
        # Field-level validation errors from a serializer
        message = "Validation failed. Please check the highlighted fields."
        details = detail
    else:
        message = detail.get("detail") if isinstance(detail, dict) else str(detail)
        details = None

    payload = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details

    response.data = payload
    return response
