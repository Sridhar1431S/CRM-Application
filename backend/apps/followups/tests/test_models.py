from django.test import TestCase

from apps.followups.models import FollowUp
from tests.factories import create_customer, create_followup, create_opportunity, create_sales_rep


class FollowUpModelTests(TestCase):
    def test_str_mentions_the_opportunity(self):
        opportunity = create_opportunity(customer=create_customer(company_name="Acme Corp"))

        followup = create_followup(opportunity=opportunity)

        self.assertIn("Acme Corp", str(followup))

    def test_followups_are_deleted_with_their_opportunity(self):
        followup = create_followup()

        followup.opportunity.delete()

        self.assertFalse(FollowUp.objects.filter(pk=followup.pk).exists())

    def test_author_deletion_keeps_the_followup(self):
        rep = create_sales_rep()
        followup = create_followup(created_by=rep)

        rep.delete()

        followup.refresh_from_db()
        self.assertIsNone(followup.created_by)
