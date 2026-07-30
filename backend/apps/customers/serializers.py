from rest_framework import serializers

from apps.customers.models import Customer
from core.validators import validate_phone_number


class CustomerSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])

    class Meta:
        model = Customer
        fields = [
            "id",
            "company_name",
            "contact_person",
            "email",
            "phone_number",
            "industry",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Company name is required.")
        return value.strip()

    def validate_contact_person(self, value):
        if not value.strip():
            raise serializers.ValidationError("Contact person is required.")
        return value.strip()

    def validate_email(self, value):
        value = value.lower().strip()
        qs = Customer.all_objects.filter(email__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A customer with this email already exists.")
        return value


class CustomerListSerializer(CustomerSerializer):
    """
    Lightweight variant for list views. Currently identical to the detail
    serializer since Customer has no heavy nested relations, but kept
    separate so list-specific trimming can be added later without touching
    the detail contract.
    """

    pass
