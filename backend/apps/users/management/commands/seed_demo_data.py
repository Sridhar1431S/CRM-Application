import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.customers.models import Customer
from apps.followups.models import FollowUp
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.users.models import User


class Command(BaseCommand):
    help = "Seeds the database with a demo administrator, sales reps, customers, leads, and opportunities."

    @transaction.atomic
    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            email="admin@crmlite.com",
            defaults={"name": "Alex Admin", "role": User.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("Admin@12345")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin: admin@crmlite.com / Admin@12345"))

        reps_data = [
            ("Priya Sharma", "priya@crmlite.com"),
            ("Rohan Verma", "rohan@crmlite.com"),
            ("Ananya Iyer", "ananya@crmlite.com"),
        ]
        reps = []
        for name, email in reps_data:
            rep, created = User.objects.get_or_create(
                email=email, defaults={"name": name, "role": User.Role.SALES_REP}
            )
            if created:
                rep.set_password("Rep@12345")
                rep.save()
            reps.append(rep)
        self.stdout.write(self.style.SUCCESS(f"Sales reps ready ({len(reps)}). Password: Rep@12345"))

        industries = ["SaaS", "Manufacturing", "Retail", "Healthcare", "Finance", "Education"]
        statuses = [Customer.Status.PROSPECT, Customer.Status.ACTIVE, Customer.Status.INACTIVE]
        customers = []
        for i in range(1, 13):
            customer, _ = Customer.objects.get_or_create(
                email=f"contact{i}@customer{i}.com",
                defaults={
                    "company_name": f"Customer Company {i}",
                    "contact_person": f"Contact Person {i}",
                    "phone_number": f"+91 90000{i:05d}",
                    "industry": random.choice(industries),
                    "status": random.choice(statuses),
                },
            )
            customers.append(customer)
        self.stdout.write(self.style.SUCCESS(f"Customers ready ({len(customers)})."))

        sources = ["Website", "Referral", "Cold Call", "Event", "Social Media"]
        priorities = [Lead.Priority.LOW, Lead.Priority.MEDIUM, Lead.Priority.HIGH]
        lead_statuses = [Lead.Status.NEW, Lead.Status.CONTACTED, Lead.Status.QUALIFIED]
        leads = []
        for i in range(1, 16):
            lead, _ = Lead.objects.get_or_create(
                email=f"lead{i}@prospect{i}.com",
                defaults={
                    "company_name": f"Prospect Inc {i}",
                    "contact_name": f"Lead Contact {i}",
                    "phone_number": f"+91 91111{i:05d}",
                    "source": random.choice(sources),
                    "priority": random.choice(priorities),
                    "status": random.choice(lead_statuses),
                    "assigned_rep": random.choice(reps) if i % 3 else None,
                },
            )
            leads.append(lead)
        self.stdout.write(self.style.SUCCESS(f"Leads ready ({len(leads)})."))

        stages = [
            Opportunity.Stage.QUALIFICATION,
            Opportunity.Stage.PROPOSAL,
            Opportunity.Stage.NEGOTIATION,
            Opportunity.Stage.WON,
            Opportunity.Stage.LOST,
        ]
        opportunities = []
        for i, customer in enumerate(customers):
            opp, created = Opportunity.objects.get_or_create(
                customer=customer,
                defaults={
                    "assigned_rep": reps[i % len(reps)],
                    "estimated_value": random.randint(5, 200) * 1000,
                    "expected_closing_date": timezone.localdate() + timedelta(days=random.randint(5, 90)),
                    "stage": random.choice(stages),
                },
            )
            opportunities.append(opp)
        self.stdout.write(self.style.SUCCESS(f"Opportunities ready ({len(opportunities)})."))

        followup_count = 0
        for opp in opportunities[:6]:
            FollowUp.objects.get_or_create(
                opportunity=opp,
                note="Initial discovery call completed, sending proposal next.",
                defaults={
                    "next_followup_date": timezone.localdate() + timedelta(days=random.randint(0, 5)),
                    "created_by": opp.assigned_rep,
                },
            )
            followup_count += 1
        self.stdout.write(self.style.SUCCESS(f"Follow-ups ready ({followup_count})."))

        self.stdout.write(self.style.SUCCESS("Seed complete."))
