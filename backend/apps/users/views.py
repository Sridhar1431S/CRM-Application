import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import LoginSerializer, RegisterSerializer, UserSerializer

logger = logging.getLogger("crm_lite")

REFRESH_COOKIE_NAME = "refresh_token"


def _refresh_cookie_kwargs():
    return dict(
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path="/api/auth/",
    )


class RegisterView(APIView):
    """POST /api/auth/register"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = Response(
            {"user": UserSerializer(user).data, "detail": "Account created successfully."},
            status=status.HTTP_201_CREATED,
        )
        return response


class LoginView(APIView):
    """
    POST /api/auth/login

    Authenticates a user and returns a short-lived access token in the
    response body plus a long-lived refresh token in an httpOnly cookie.
    Keeping the refresh token out of JS-accessible storage mitigates XSS
    token theft while `localStorage`-based access tokens stay short-lived.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        response = Response(
            {"access": str(data["access"]), "user": data["user"]},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(REFRESH_COOKIE_NAME, str(data["refresh"]), **_refresh_cookie_kwargs())
        return response


class RefreshView(APIView):
    """
    POST /api/auth/refresh

    Reads the refresh token from the httpOnly cookie (not the request body)
    and issues a new access token. Supports `ROTATE_REFRESH_TOKENS` so a
    fresh refresh cookie is written back on every call, enabling persistent
    login across browser sessions until the token is rotated out or revoked.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        raw_token = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if not raw_token:
            return Response({"detail": "Refresh token missing."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(raw_token)
        except TokenError:
            return Response({"detail": "Refresh token invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)

        access = refresh.access_token
        response = Response({"access": str(access)}, status=status.HTTP_200_OK)

        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS"):
            response.set_cookie(REFRESH_COOKIE_NAME, str(refresh), **_refresh_cookie_kwargs())

        return response


class LogoutView(APIView):
    """
    POST /api/auth/logout

    Blacklists the current refresh token (if blacklisting is enabled) and
    clears the cookie so the browser cannot silently re-authenticate.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_token = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if raw_token:
            try:
                RefreshToken(raw_token).blacklist()
            except TokenError:
                # Already expired/blacklisted: the cookie is cleared below either
                # way, but the failure must not disappear without a trace.
                logger.warning("Logout could not blacklist refresh token", exc_info=True)

        response = Response({"detail": "Logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/auth/")
        return response


class MeView(APIView):
    """GET /api/auth/me — returns the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
