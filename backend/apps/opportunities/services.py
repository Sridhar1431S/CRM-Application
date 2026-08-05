from apps.opportunities.models import Opportunity
from core.access import is_admin_or_assigned_rep
from core.exceptions import BusinessRuleViolation

TERMINAL_STAGES = {Opportunity.Stage.WON, Opportunity.Stage.LOST}


class OpportunityService:
    """
    Central place for opportunity stage-transition rules so they cannot be
    bypassed by hitting the update action from a different code path.

    Rules enforced (from the assignment spec):
      1. Won/Lost opportunities cannot move to any other stage (interpreted
         broadly from "cannot be moved back to Qualification" -- once a deal
         is closed, closed-won/closed-lost is treated as terminal, which is
         the standard CRM convention and prevents silently reopening deals
         that fed into revenue/pipeline reporting).
      2. Only the assigned representative (or an administrator) may update
         an opportunity's stage.
    """

    @staticmethod
    def update_stage(opportunity: Opportunity, new_stage: str, *, actor) -> Opportunity:
        if not is_admin_or_assigned_rep(actor, opportunity):
            raise BusinessRuleViolation("Only the assigned sales representative may update this opportunity.")

        if opportunity.stage in TERMINAL_STAGES and new_stage != opportunity.stage:
            raise BusinessRuleViolation("Won or Lost opportunities cannot be moved to another stage.")

        opportunity.stage = new_stage
        opportunity.save(update_fields=["stage", "updated_at"])
        return opportunity
