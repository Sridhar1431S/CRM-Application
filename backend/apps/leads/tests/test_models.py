from django.test import TestCase

from apps.leads.models import Lead
from tests.factories import create_lead


class LeadModelTests(TestCase):
    def test_str_includes_company_and_contact_name(self):
        lead = create_lead(company_name="Prospect Inc", contact_name="Ravi Kumar")

        self.assertEqual(str(lead), "Prospect Inc (Ravi Kumar)")

    def test_defaults(self):
        lead = create_lead()

        self.assertEqual(lead.status, Lead.Status.NEW)
        self.assertEqual(lead.priority, Lead.Priority.MEDIUM)
        self.assertFalse(lead.converted_to_opportunity)
        self.assertIsNone(lead.assigned_rep)
