from rest_framework import serializers

from apps.followups.models import FollowUp
from apps.users.serializers import UserSerializer


class FollowUpSerializer(serializers.ModelSerializer):
    created_by_detail = UserSerializer(source="created_by", read_only=True)

    class Meta:
        model = FollowUp
        fields = [
            "id",
            "opportunity",
            "note",
            "next_followup_date",
            "created_by",
            "created_by_detail",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate_note(self, value):
        if not value.strip():
            raise serializers.ValidationError("Follow-up note cannot be empty.")
        return value.strip()
