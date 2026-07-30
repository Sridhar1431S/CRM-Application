import uuid

from django.conf import settings
from django.db import models


class Opportunity(models.Model):
    class Stage(models.TextChoices):
        QUALIFICATION = "qualification", "Qualification"
        PROPOSAL = "proposal", "Proposal"
        NEGOTIATION = "negotiation", "Negotiation"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, related_name="opportunities"
    )
    assigned_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="opportunities",
        limit_choices_to={"role": "sales_rep"},
    )
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2)
    expected_closing_date = models.DateField()
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.QUALIFICATION, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "opportunities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["stage"]),
            models.Index(fields=["assigned_rep", "stage"]),
        ]

    def __str__(self):
        return f"{self.customer.company_name} - {self.get_stage_display()}"

    @property
    def is_open(self):
        return self.stage not in (self.Stage.WON, self.Stage.LOST)
