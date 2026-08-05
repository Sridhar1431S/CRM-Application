from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["name", "email", "password", "password_confirm"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        try:
            validate_password(attrs["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        # Role is never client-controlled on the public endpoint; elevating a
        # user to Administrator is an admin-only operation.
        return User.objects.create_user(
            email=validated_data.pop("email"),
            password=password,
            role=User.Role.SALES_REP,
            **validated_data,
        )


class UserSerializer(serializers.ModelSerializer):
    """Read representation of a user, embedded in dashboard/opportunity payloads."""

    class Meta:
        model = User
        fields = ["id", "name", "email", "role", "is_active", "created_at"]
        read_only_fields = fields


class LoginSerializer(TokenObtainPairSerializer):
    """
    Extends SimpleJWT's default token serializer to:
      * authenticate by email instead of username
      * reject disabled accounts with a clear message
      * embed basic user/role info in the token response so the frontend
        doesn't need a second round trip after login
    """

    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}, code="authorization"
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "This account has been disabled. Contact an administrator."},
                code="authorization",
            )

        data = super().validate(attrs)
        data["user"] = UserSerializer(user).data
        return data
