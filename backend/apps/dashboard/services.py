from apps.customers.models import Customer
from apps.followups.models import FollowUp
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.users.models import User

OPEN_STAGES = [Opportunity.Stage.QUALIFICATION, Opportunity.Stage.PROPOSAL, Opportunity.Stage.NEGOTIATION]


class DashboardService:
    @staticmethod
    def admin_summary() -> dict:
        """
        Matches the assignment's Administrator Dashboard spec exactly:
        Total Customers, Total Leads, Open Opportunities, Active Sales Reps.
        """
        return {
            "total_customers": Customer.objects.count(),
            "total_leads": Lead.objects.filter(deleted_at__isnull=True).count(),
            "open_opportunities": Opportunity.objects.filter(stage__in=OPEN_STAGES).count(),
            "active_sales_representatives": User.objects.filter(
                role=User.Role.SALES_REP, is_active=True
            ).count(),
        }

    @staticmethod
    def progress_monitoring() -> list:
        """
        Consolidated sales-activity table for admins:
        Customer | Sales Representative | Opportunity(id) | Stage | Value | Expected Close.
        Always reflects the latest data since it queries live, not a cached snapshot.
        """
        rows = []
        opportunities = Opportunity.objects.select_related("customer", "assigned_rep").order_by("-updated_at")
        for opp in opportunities:
            rows.append(
                {
                    "opportunity_id": str(opp.id),
                    "customer": opp.customer.company_name,
                    "sales_representative": opp.assigned_rep.name if opp.assigned_rep else None,
                    "stage": opp.stage,
                    "value": str(opp.estimated_value),
                    "expected_close": opp.expected_closing_date,
                }
            )
        return rows

    @staticmethod
    def sales_rep_summary(user) -> dict:
        """
        Matches the assignment's Sales Representative Dashboard spec exactly:
        Assigned Customers, Assigned Leads, Open Opportunities, Follow-ups Due Today.
        "Assigned Customers" is derived as the distinct set of customers behind
        this rep's opportunities, since Customer has no direct owner field in
        the spec (only Opportunity/Lead carry an assigned_rep FK).
        """
        from django.utils import timezone

        assigned_customer_count = (
            Opportunity.objects.filter(assigned_rep=user).values("customer_id").distinct().count()
        )
        assigned_leads = Lead.objects.filter(assigned_rep=user, deleted_at__isnull=True).count()
        open_opportunities = Opportunity.objects.filter(assigned_rep=user, stage__in=OPEN_STAGES).count()
        followups_due_today = FollowUp.objects.filter(
            opportunity__assigned_rep=user, next_followup_date=timezone.localdate()
        ).count()

        return {
            "assigned_customers": assigned_customer_count,
            "assigned_leads": assigned_leads,
            "open_opportunities": open_opportunities,
            "followups_due_today": followups_due_today,
        }
