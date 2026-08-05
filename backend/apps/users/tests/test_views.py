from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.views import REFRESH_COOKIE_NAME
from tests.factories import create_sales_rep

# The auth flow needs more requests than the production anonymous throttle
# (30/minute) allows, and rate limiting is not what these tests assert.
UNTHROTTLED = {**settings.REST_FRAMEWORK, "DEFAULT_THROTTLE_CLASSES": []}


@override_settings(REST_FRAMEWORK=UNTHROTTLED)
class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rep = create_sales_rep(email="priya@crmlite.test", password="Rep@12345")

    def _login(self):
        return self.client.post(
            reverse("users:login"),
            {"email": self.rep.email, "password": "Rep@12345"},
            format="json",
        )

    def test_register_creates_an_account(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "New Rep",
                "email": "new@crmlite.test",
                "password": "Password123!",
                "password_confirm": "Password123!",
                "role": "sales_rep",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["email"], "new@crmlite.test")

    def test_login_returns_access_token_and_httponly_refresh_cookie(self):
        response = self._login()

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["email"], self.rep.email)

        cookie = response.cookies[REFRESH_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["path"], "/api/auth/")

    def test_login_with_bad_credentials_returns_400_envelope(self):
        response = self.client.post(
            reverse("users:login"),
            {"email": self.rep.email, "password": "nope"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email or password.", str(response.data["error"]["message"]))
        self.assertNotIn(REFRESH_COOKIE_NAME, response.cookies)

    def test_refresh_reads_the_cookie_and_issues_a_new_access_token(self):
        self._login()

        response = self.client.post(reverse("users:refresh"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn(REFRESH_COOKIE_NAME, response.cookies)

    def test_refresh_without_a_cookie_is_unauthorized(self):
        response = self.client.post(reverse("users:refresh"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Refresh token missing.")

    def test_refresh_with_an_invalid_cookie_is_unauthorized(self):
        self.client.cookies[REFRESH_COOKIE_NAME] = "not-a-token"

        response = self.client.post(reverse("users:refresh"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Refresh token invalid or expired.")

    def test_logout_blacklists_the_refresh_token_and_clears_the_cookie(self):
        access = self._login().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(reverse("users:logout"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies[REFRESH_COOKIE_NAME].value, "")

        self.client.credentials()
        self.assertEqual(self.client.post(reverse("users:refresh")).status_code, 401)

    def test_logout_tolerates_an_invalid_refresh_cookie(self):
        access = self._login().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.client.cookies[REFRESH_COOKIE_NAME] = "not-a-token"

        response = self.client.post(reverse("users:logout"))

        self.assertEqual(response.status_code, 200)

    def test_logout_without_a_refresh_cookie_still_succeeds(self):
        access = self._login().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        del self.client.cookies[REFRESH_COOKIE_NAME]

        response = self.client.post(reverse("users:logout"))

        self.assertEqual(response.status_code, 200)

    def test_refresh_does_not_reset_the_cookie_when_rotation_is_disabled(self):
        self._login()

        with override_settings(SIMPLE_JWT={**settings.SIMPLE_JWT, "ROTATE_REFRESH_TOKENS": False}):
            response = self.client.post(reverse("users:refresh"))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(REFRESH_COOKIE_NAME, response.cookies)

    def test_me_returns_the_authenticated_user(self):
        access = self._login().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.get(reverse("users:me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.rep.email)

    def test_me_requires_authentication(self):
        self.assertEqual(self.client.get(reverse("users:me")).status_code, 401)
