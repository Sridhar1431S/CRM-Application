import uuid

from django.conf import settings
from django.db import models


class FollowUp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    opportunity = models.ForeignKey(
        "opportunities.Opportunity", on_delete=models.CASCADE, related_name="followups"
    )
    note = models.TextField()
    next_followup_date = models.DateField(null=True, blank=True, db_index=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="followups_logged"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "followups"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["next_followup_date"]),
            models.Index(fields=["opportunity", "-created_at"]),
        ]

    def __str__(self):
        return f"Follow-up on {self.opportunity} at {self.created_at:%Y-%m-%d}"
