from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.followups.models import FollowUp
from apps.followups.services import FollowUpService
from core.exceptions import BusinessRuleViolation
from tests.factories import create_admin, create_opportunity, create_sales_rep


class CreateFollowUpTests(TestCase):
    def setUp(self):
        self.admin = create_admin()
        self.rep = create_sales_rep()
        self.other_rep = create_sales_rep()
        self.opportunity = create_opportunity(assigned_rep=self.rep)
        self.next_date = timezone.localdate() + timedelta(days=3)

    def test_assigned_rep_can_log_a_followup(self):
        followup = FollowUpService.create_followup(
            self.opportunity, note="Called the client.", next_followup_date=self.next_date, actor=self.rep
        )

        self.assertEqual(followup.opportunity, self.opportunity)
        self.assertEqual(followup.created_by, self.rep)
        self.assertEqual(followup.next_followup_date, self.next_date)

    def test_admin_can_log_a_followup_on_any_opportunity(self):
        followup = FollowUpService.create_followup(
            self.opportunity, note="Escalated.", next_followup_date=None, actor=self.admin
        )

        self.assertEqual(followup.created_by, self.admin)
        self.assertIsNone(followup.next_followup_date)

    def test_other_rep_cannot_log_a_followup(self):
        with self.assertRaises(BusinessRuleViolation):
            FollowUpService.create_followup(
                self.opportunity, note="Poaching.", next_followup_date=None, actor=self.other_rep
            )

        self.assertFalse(FollowUp.objects.exists())

    def test_unassigned_opportunity_accepts_only_admin_followups(self):
        opportunity = create_opportunity(assigned_rep=None)

        with self.assertRaises(BusinessRuleViolation):
            FollowUpService.create_followup(
                opportunity, note="Orphan.", next_followup_date=None, actor=self.rep
            )

        followup = FollowUpService.create_followup(
            opportunity, note="Reassign needed.", next_followup_date=None, actor=self.admin
        )
        self.assertEqual(followup.opportunity, opportunity)
