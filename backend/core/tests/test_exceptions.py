import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from django.test import SimpleTestCase
from rest_framework import exceptions as drf_exceptions
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from core.exceptions import BusinessRuleViolation, global_exception_handler


class GlobalExceptionHandlerTests(SimpleTestCase):
    def setUp(self):
        self.context = {"view": APIView(), "request": APIRequestFactory().get("/")}

    def _handle(self, exc):
        return global_exception_handler(exc, self.context)

    def test_http404_becomes_not_found_envelope(self):
        response = self._handle(Http404("missing"))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"]["code"], "not_found")
        self.assertNotIn("details", response.data["error"])

    def test_django_permission_denied_becomes_403_envelope(self):
        response = self._handle(PermissionDenied("nope"))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["error"]["code"], "permission_denied")

    def test_django_validation_error_is_translated_with_field_details(self):
        response = self._handle(DjangoValidationError({"email": ["Enter a valid email address."]}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "invalid")
        self.assertEqual(
            response.data["error"]["message"], "Validation failed. Please check the highlighted fields."
        )
        self.assertEqual(response.data["error"]["details"], {"email": ["Enter a valid email address."]})

    def test_business_rule_violation_returns_422_with_message(self):
        response = self._handle(BusinessRuleViolation("Won opportunities are terminal."))

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "business_rule_violation")
        self.assertEqual(response.data["error"]["message"], "Won opportunities are terminal.")

    def test_drf_validation_error_with_non_field_detail_keeps_message(self):
        response = self._handle(drf_exceptions.ValidationError({"detail": "Invalid email or password."}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["message"], "Invalid email or password.")

    def test_unhandled_exception_is_logged_and_returns_generic_500(self):
        with self.assertLogs("crm_lite", level=logging.ERROR):
            response = self._handle(RuntimeError("boom"))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data["error"]["code"], "internal_server_error")
        self.assertEqual(
            response.data["error"]["message"],
            "An unexpected error occurred. Please try again later.",
        )
