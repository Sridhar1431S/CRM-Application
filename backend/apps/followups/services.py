from apps.followups.models import FollowUp
from core.access import is_admin_or_assigned_rep
from core.exceptions import BusinessRuleViolation


class FollowUpService:
    @staticmethod
    def create_followup(opportunity, *, note, next_followup_date, actor) -> FollowUp:
        if not is_admin_or_assigned_rep(actor, opportunity):
            raise BusinessRuleViolation(
                "Only the assigned sales representative may log a follow-up for this opportunity."
            )
        return FollowUp.objects.create(
            opportunity=opportunity,
            note=note,
            next_followup_date=next_followup_date,
            created_by=actor,
        )
