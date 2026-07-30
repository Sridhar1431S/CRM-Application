from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import User


class SalesRepSerializer(serializers.ModelSerializer):
    """
    Sales representatives are simply Users with role=sales_rep. We deliberately
    did not introduce a separate SalesRepProfile table: the assignment's
    required fields (Name, Email, Status) map 1:1 onto columns that already
    exist on User, and adding a profile table would just be a redundant
    join for no additional data. This keeps the schema DRY.
    """

    class Meta:
        model = User
        fields = ["id", "name", "email", "is_active", "role", "created_at", "updated_at"]
        read_only_fields = ["id", "role", "created_at", "updated_at"]


class SalesRepCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "name", "email", "password", "is_active"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(role=User.Role.SALES_REP, **validated_data)
        user.set_password(password)
        user.save()
        return user
