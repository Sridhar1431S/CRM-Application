from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from core.validators import validate_phone_number


class ValidatePhoneNumberTests(SimpleTestCase):
    def test_accepts_international_and_punctuated_formats(self):
        for value in ["+91 9000000001", "(080) 4123-4567", "9000000001", "+1-555-000-0000"]:
            with self.subTest(value=value):
                self.assertIsNone(validate_phone_number(value))

    def test_rejects_too_short_too_long_and_illegal_characters(self):
        for value in ["12345", "9" * 21, "+91 90000abcd", "", "+91,9000000001"]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validate_phone_number(value)
