from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.customers.models import Customer
from apps.followups.models import FollowUp
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.users.models import User


class SeedDemoDataCommandTests(TestCase):
    def test_seeds_demo_users_and_pipeline_data(self):
        call_command("seed_demo_data", stdout=StringIO())

        admin = User.objects.get(email="admin@crmlite.com")
        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertTrue(admin.check_password("Admin@12345"))
        self.assertTrue(admin.is_staff)

        rep = User.objects.get(email="priya@crmlite.com")
        self.assertEqual(rep.role, User.Role.SALES_REP)
        self.assertTrue(rep.check_password("Rep@12345"))

        self.assertEqual(Customer.objects.count(), 12)
        self.assertEqual(Lead.objects.count(), 15)
        self.assertEqual(Opportunity.objects.count(), 12)
        self.assertEqual(FollowUp.objects.count(), 6)

    def test_running_twice_is_idempotent(self):
        call_command("seed_demo_data", stdout=StringIO())
        call_command("seed_demo_data", stdout=StringIO())

        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(Customer.objects.count(), 12)
        self.assertEqual(Lead.objects.count(), 15)
        self.assertEqual(Opportunity.objects.count(), 12)
        self.assertEqual(FollowUp.objects.count(), 6)
