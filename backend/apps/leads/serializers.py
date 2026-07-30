from rest_framework import serializers

from apps.leads.models import Lead
from apps.users.models import User
from apps.users.serializers import UserSerializer
from core.validators import validate_phone_number


class LeadSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    assigned_rep_detail = UserSerializer(source="assigned_rep", read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "company_name",
            "contact_name",
            "email",
            "phone_number",
            "source",
            "priority",
            "status",
            "assigned_rep",
            "assigned_rep_detail",
            "converted_to_opportunity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "converted_to_opportunity", "created_at", "updated_at"]

    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Company name is required.")
        return value.strip()

    def validate_contact_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Contact name is required.")
        return value.strip()

    def validate_assigned_rep(self, value):
        if value is not None and value.role != User.Role.SALES_REP:
            raise serializers.ValidationError("Leads can only be assigned to a sales representative.")
        return value


class LeadAssignSerializer(serializers.Serializer):
    assigned_rep = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.SALES_REP, is_active=True)
    )
