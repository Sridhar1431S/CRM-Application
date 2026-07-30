from django.utils import timezone
from rest_framework import serializers

from apps.customers.serializers import CustomerSerializer
from apps.opportunities.models import Opportunity
from apps.users.models import User
from apps.users.serializers import UserSerializer


class OpportunitySerializer(serializers.ModelSerializer):
    customer_detail = CustomerSerializer(source="customer", read_only=True)
    assigned_rep_detail = UserSerializer(source="assigned_rep", read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "customer",
            "customer_detail",
            "assigned_rep",
            "assigned_rep_detail",
            "estimated_value",
            "expected_closing_date",
            "stage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_estimated_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Opportunity value must be greater than zero.")
        return value

    def validate_expected_closing_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Expected closing date cannot be in the past.")
        return value

    def validate_assigned_rep(self, value):
        if value is not None and value.role != User.Role.SALES_REP:
            raise serializers.ValidationError("Opportunities can only be assigned to a sales representative.")
        return value

    def validate_stage(self, value):
        """
        Field-level guard for the obvious case (serializer-only usage).
        The authoritative check -- including "who is allowed to change it"
        -- lives in OpportunityService.update_stage, which the ViewSet's
        stage-update action always goes through.
        """
        if self.instance is not None:
            current = self.instance.stage
            if current in (Opportunity.Stage.WON, Opportunity.Stage.LOST) and value != current:
                raise serializers.ValidationError(
                    "Won or Lost opportunities cannot be moved to another stage."
                )
        return value


class OpportunityStageUpdateSerializer(serializers.Serializer):
    stage = serializers.ChoiceField(choices=Opportunity.Stage.choices)
