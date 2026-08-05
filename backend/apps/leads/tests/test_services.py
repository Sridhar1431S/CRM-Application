from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.customers.models import Customer
from apps.leads.models import Lead
from apps.leads.services import LeadService
from apps.opportunities.models import Opportunity
from core.exceptions import BusinessRuleViolation
from tests.factories import create_admin, create_customer, create_lead, create_sales_rep


class AssignLeadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rep = create_sales_rep()

    def test_new_lead_moves_to_contacted_on_assignment(self):
        lead = create_lead(status=Lead.Status.NEW)

        LeadService.assign(lead, self.rep)

        lead.refresh_from_db()
        self.assertEqual(lead.assigned_rep, self.rep)
        self.assertEqual(lead.status, Lead.Status.CONTACTED)

    def test_non_new_status_is_preserved_on_reassignment(self):
        lead = create_lead(status=Lead.Status.QUALIFIED, assigned_rep=create_sales_rep())

        LeadService.assign(lead, self.rep)

        lead.refresh_from_db()
        self.assertEqual(lead.assigned_rep, self.rep)
        self.assertEqual(lead.status, Lead.Status.QUALIFIED)


class ConvertLeadToOpportunityTests(TestCase):
    def setUp(self):
        self.admin = create_admin()
        self.rep = create_sales_rep()
        self.future_date = timezone.localdate() + timedelta(days=30)

    def _convert(self, lead, **overrides):
        kwargs = {
            "estimated_value": "50000.00",
            "expected_closing_date": self.future_date,
            "actor": self.admin,
        }
        kwargs.update(overrides)
        return LeadService.convert_to_opportunity(lead, **kwargs)

    def test_conversion_creates_customer_and_qualification_stage_opportunity(self):
        lead = create_lead(assigned_rep=self.rep, email="prospect@newco.test")

        opportunity = self._convert(lead)
        opportunity.refresh_from_db()

        self.assertEqual(opportunity.stage, Opportunity.Stage.QUALIFICATION)
        self.assertEqual(opportunity.assigned_rep, self.rep)
        self.assertEqual(opportunity.estimated_value, Decimal("50000.00"))
        self.assertEqual(opportunity.customer.email, "prospect@newco.test")
        self.assertEqual(opportunity.customer.status, Customer.Status.PROSPECT)

        lead.refresh_from_db()
        self.assertTrue(lead.converted_to_opportunity)
        self.assertEqual(lead.status, Lead.Status.QUALIFIED)

    def test_conversion_reuses_existing_customer_matched_by_email(self):
        customer = create_customer(email="prospect@newco.test")
        lead = create_lead(assigned_rep=self.rep, email="prospect@newco.test")

        opportunity = self._convert(lead)

        self.assertEqual(opportunity.customer, customer)
        self.assertEqual(Customer.all_objects.filter(email="prospect@newco.test").count(), 1)

    def test_conversion_restores_a_soft_deleted_customer(self):
        customer = create_customer(email="prospect@newco.test", deleted_at=timezone.now())
        lead = create_lead(assigned_rep=self.rep, email="prospect@newco.test")

        opportunity = self._convert(lead)

        customer.refresh_from_db()
        self.assertIsNone(customer.deleted_at)
        self.assertEqual(opportunity.customer, customer)

    def test_already_converted_lead_is_rejected(self):
        lead = create_lead(assigned_rep=self.rep, converted_to_opportunity=True)

        with self.assertRaises(BusinessRuleViolation):
            self._convert(lead)

    def test_lost_lead_is_rejected(self):
        lead = create_lead(assigned_rep=self.rep, status=Lead.Status.LOST)

        with self.assertRaises(BusinessRuleViolation):
            self._convert(lead)

    def test_unassigned_lead_is_rejected(self):
        lead = create_lead()

        with self.assertRaises(BusinessRuleViolation):
            self._convert(lead)

    def test_non_numeric_estimated_value_is_rejected(self):
        lead = create_lead(assigned_rep=self.rep)

        with self.assertRaises(BusinessRuleViolation):
            self._convert(lead, estimated_value="not-a-number")

    def test_non_positive_estimated_value_is_rejected(self):
        lead = create_lead(assigned_rep=self.rep)

        with self.assertRaises(BusinessRuleViolation):
            self._convert(lead, estimated_value="0")

    def test_past_closing_date_is_rejected(self):
        lead = create_lead(assigned_rep=self.rep)

        with self.assertRaises(BusinessRuleViolation):
            self._convert(lead, expected_closing_date=timezone.localdate() - timedelta(days=1))

    def test_rejected_conversion_creates_no_customer_or_opportunity(self):
        lead = create_lead(assigned_rep=self.rep, email="prospect@newco.test")

        with self.assertRaises(BusinessRuleViolation):
            self._convert(lead, estimated_value="-5")

        self.assertFalse(Customer.all_objects.filter(email="prospect@newco.test").exists())
        self.assertFalse(Opportunity.objects.exists())
