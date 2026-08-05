from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.dashboard.services import DashboardService
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from tests.factories import (
    create_admin,
    create_customer,
    create_followup,
    create_lead,
    create_opportunity,
    create_sales_rep,
)


class AdminSummaryTests(TestCase):
    def test_counts_only_live_records_and_open_opportunities(self):
        create_admin()
        rep = create_sales_rep()
        create_sales_rep(is_active=False)

        customer = create_customer()
        create_customer(deleted_at=timezone.now())

        create_lead()
        create_lead(deleted_at=timezone.now())

        create_opportunity(customer=customer, assigned_rep=rep, stage=Opportunity.Stage.PROPOSAL)
        create_opportunity(customer=customer, assigned_rep=rep, stage=Opportunity.Stage.WON)
        create_opportunity(customer=customer, assigned_rep=rep, stage=Opportunity.Stage.LOST)

        summary = DashboardService.admin_summary()

        self.assertEqual(summary["total_customers"], 1)
        self.assertEqual(summary["total_leads"], 1)
        self.assertEqual(summary["open_opportunities"], 1)
        self.assertEqual(summary["active_sales_representatives"], 1)


class ProgressMonitoringTests(TestCase):
    def test_row_shape_and_unassigned_opportunity_handling(self):
        rep = create_sales_rep(name="Priya Sharma")
        customer = create_customer(company_name="Acme Corp")
        opportunity = create_opportunity(
            customer=customer,
            assigned_rep=rep,
            stage=Opportunity.Stage.NEGOTIATION,
            estimated_value=75000,
        )
        create_opportunity(assigned_rep=None)

        rows = DashboardService.progress_monitoring()

        self.assertEqual(len(rows), 2)
        row = next(r for r in rows if r["opportunity_id"] == str(opportunity.id))
        self.assertEqual(row["customer"], "Acme Corp")
        self.assertEqual(row["sales_representative"], "Priya Sharma")
        self.assertEqual(row["stage"], Opportunity.Stage.NEGOTIATION)
        self.assertEqual(row["value"], "75000.00")
        self.assertEqual(row["expected_close"], opportunity.expected_closing_date)
        self.assertIsNone(next(r for r in rows if r["opportunity_id"] != str(opportunity.id))[
            "sales_representative"
        ])

    def test_rows_are_ordered_by_most_recently_updated(self):
        older = create_opportunity()
        newer = create_opportunity()
        older.stage = Opportunity.Stage.PROPOSAL
        older.save(update_fields=["stage", "updated_at"])

        rows = DashboardService.progress_monitoring()

        self.assertEqual(
            [row["opportunity_id"] for row in rows], [str(older.id), str(newer.id)]
        )


class SalesRepSummaryTests(TestCase):
    def test_scopes_every_metric_to_the_requesting_rep(self):
        rep = create_sales_rep()
        other_rep = create_sales_rep()

        customer = create_customer()
        create_opportunity(customer=customer, assigned_rep=rep, stage=Opportunity.Stage.PROPOSAL)
        create_opportunity(customer=customer, assigned_rep=rep, stage=Opportunity.Stage.WON)
        own_open = create_opportunity(assigned_rep=rep, stage=Opportunity.Stage.QUALIFICATION)
        create_opportunity(assigned_rep=other_rep, stage=Opportunity.Stage.PROPOSAL)

        create_lead(assigned_rep=rep, status=Lead.Status.CONTACTED)
        create_lead(assigned_rep=rep, deleted_at=timezone.now())
        create_lead(assigned_rep=other_rep)

        create_followup(opportunity=own_open, next_followup_date=timezone.localdate())
        create_followup(
            opportunity=own_open, next_followup_date=timezone.localdate() + timedelta(days=1)
        )

        summary = DashboardService.sales_rep_summary(rep)

        self.assertEqual(summary["assigned_customers"], 2)
        self.assertEqual(summary["assigned_leads"], 1)
        self.assertEqual(summary["open_opportunities"], 2)
        self.assertEqual(summary["followups_due_today"], 1)

    def test_rep_without_any_work_gets_zeroes(self):
        summary = DashboardService.sales_rep_summary(create_sales_rep())

        self.assertEqual(
            summary,
            {
                "assigned_customers": 0,
                "assigned_leads": 0,
                "open_opportunities": 0,
                "followups_due_today": 0,
            },
        )
