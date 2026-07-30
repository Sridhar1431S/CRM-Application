from django.db import transaction
from django.utils import timezone

from apps.leads.models import Lead
from core.exceptions import BusinessRuleViolation


class LeadService:
    @staticmethod
    def assign(lead: Lead, rep) -> Lead:
        lead.assigned_rep = rep
        if lead.status == Lead.Status.NEW:
            lead.status = Lead.Status.CONTACTED
        lead.save(update_fields=["assigned_rep", "status", "updated_at"])
        return lead

    @staticmethod
    @transaction.atomic
    def convert_to_opportunity(lead: Lead, *, estimated_value, expected_closing_date, actor):
        """
        Converts a Lead into an Opportunity. Business rules enforced here
        rather than in the view/serializer because they span two models:
          * the lead must not already be converted (no duplicate pipeline entries)
          * the lead must not be Lost
          * the lead must have an assigned rep and a matching customer record
            is created/looked up by email so the opportunity has a Customer FK
        """
        from apps.customers.models import Customer
        from apps.opportunities.models import Opportunity

        if lead.converted_to_opportunity:
            raise BusinessRuleViolation("This lead has already been converted to an opportunity.")
        if lead.status == Lead.Status.LOST:
            raise BusinessRuleViolation("A lost lead cannot be converted to an opportunity.")
        if lead.assigned_rep is None:
            raise BusinessRuleViolation("Assign this lead to a sales representative before converting it.")

        try:
            value_decimal = float(estimated_value)
        except (TypeError, ValueError):
            raise BusinessRuleViolation("Estimated value must be a number.")
        if value_decimal <= 0:
            raise BusinessRuleViolation("Opportunity value must be greater than zero.")

        if str(expected_closing_date) < timezone.localdate().isoformat():
            raise BusinessRuleViolation("Expected closing date cannot be in the past.")

        customer, _ = Customer.all_objects.get_or_create(
            email=lead.email,
            defaults={
                "company_name": lead.company_name,
                "contact_person": lead.contact_name,
                "phone_number": lead.phone_number,
                "status": Customer.Status.PROSPECT,
            },
        )
        if customer.deleted_at is not None:
            customer.deleted_at = None
            customer.save(update_fields=["deleted_at", "updated_at"])

        opportunity = Opportunity.objects.create(
            customer=customer,
            assigned_rep=lead.assigned_rep,
            estimated_value=estimated_value,
            expected_closing_date=expected_closing_date,
            stage=Opportunity.Stage.QUALIFICATION,
        )

        lead.converted_to_opportunity = True
        lead.status = Lead.Status.QUALIFIED
        lead.save(update_fields=["converted_to_opportunity", "status", "updated_at"])

        return opportunity
