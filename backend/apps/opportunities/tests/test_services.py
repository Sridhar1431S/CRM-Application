from django.test import TestCase

from apps.opportunities.models import Opportunity
from apps.opportunities.services import OpportunityService
from core.exceptions import BusinessRuleViolation
from tests.factories import create_admin, create_opportunity, create_sales_rep


class UpdateStageTests(TestCase):
    def setUp(self):
        self.admin = create_admin()
        self.rep = create_sales_rep()
        self.other_rep = create_sales_rep()

    def test_assigned_rep_may_advance_the_stage(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.QUALIFICATION)

        OpportunityService.update_stage(opportunity, Opportunity.Stage.PROPOSAL, actor=self.rep)

        opportunity.refresh_from_db()
        self.assertEqual(opportunity.stage, Opportunity.Stage.PROPOSAL)

    def test_admin_may_advance_any_opportunity(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.PROPOSAL)

        OpportunityService.update_stage(opportunity, Opportunity.Stage.NEGOTIATION, actor=self.admin)

        opportunity.refresh_from_db()
        self.assertEqual(opportunity.stage, Opportunity.Stage.NEGOTIATION)

    def test_other_rep_cannot_update_the_stage(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.PROPOSAL)

        with self.assertRaises(BusinessRuleViolation):
            OpportunityService.update_stage(
                opportunity, Opportunity.Stage.NEGOTIATION, actor=self.other_rep
            )

        opportunity.refresh_from_db()
        self.assertEqual(opportunity.stage, Opportunity.Stage.PROPOSAL)

    def test_terminal_stages_cannot_move_to_another_stage(self):
        for terminal in [Opportunity.Stage.WON, Opportunity.Stage.LOST]:
            for target in [
                Opportunity.Stage.QUALIFICATION,
                Opportunity.Stage.PROPOSAL,
                Opportunity.Stage.NEGOTIATION,
            ]:
                with self.subTest(terminal=terminal, target=target):
                    opportunity = create_opportunity(assigned_rep=self.rep, stage=terminal)

                    with self.assertRaises(BusinessRuleViolation):
                        OpportunityService.update_stage(opportunity, target, actor=self.admin)

                    opportunity.refresh_from_db()
                    self.assertEqual(opportunity.stage, terminal)

    def test_setting_a_terminal_stage_to_itself_is_a_no_op_not_an_error(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.WON)

        OpportunityService.update_stage(opportunity, Opportunity.Stage.WON, actor=self.admin)

        opportunity.refresh_from_db()
        self.assertEqual(opportunity.stage, Opportunity.Stage.WON)

    def test_open_opportunity_may_be_closed(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.NEGOTIATION)

        OpportunityService.update_stage(opportunity, Opportunity.Stage.WON, actor=self.rep)

        opportunity.refresh_from_db()
        self.assertEqual(opportunity.stage, Opportunity.Stage.WON)
