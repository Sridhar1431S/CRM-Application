from django.db.models import ProtectedError
from django.test import TestCase

from apps.opportunities.models import Opportunity
from tests.factories import create_customer, create_opportunity, create_sales_rep


class OpportunityModelTests(TestCase):
    def test_str_includes_customer_and_stage(self):
        customer = create_customer(company_name="Acme Corp")
        opportunity = create_opportunity(customer=customer, stage=Opportunity.Stage.PROPOSAL)

        self.assertEqual(str(opportunity), "Acme Corp - Proposal")

    def test_stage_defaults_to_qualification(self):
        self.assertEqual(create_opportunity().stage, Opportunity.Stage.QUALIFICATION)

    def test_is_open_is_false_only_for_terminal_stages(self):
        for stage, expected in [
            (Opportunity.Stage.QUALIFICATION, True),
            (Opportunity.Stage.PROPOSAL, True),
            (Opportunity.Stage.NEGOTIATION, True),
            (Opportunity.Stage.WON, False),
            (Opportunity.Stage.LOST, False),
        ]:
            with self.subTest(stage=stage):
                self.assertEqual(create_opportunity(stage=stage).is_open, expected)

    def test_customer_with_opportunities_cannot_be_hard_deleted(self):
        customer = create_customer()
        create_opportunity(customer=customer)

        with self.assertRaises(ProtectedError):
            customer.delete()

    def test_deleting_the_assigned_rep_keeps_the_opportunity(self):
        rep = create_sales_rep()
        opportunity = create_opportunity(assigned_rep=rep)

        rep.delete()

        opportunity.refresh_from_db()
        self.assertIsNone(opportunity.assigned_rep)
