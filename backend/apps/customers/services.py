from apps.customers.models import Customer
from core.exceptions import BusinessRuleViolation


class CustomerService:
    """
    Encapsulates Customer business rules so the ViewSet stays a thin HTTP
    adapter. Currently the main rule enforced here (beyond serializer-level
    field validation) is protecting delete of a customer that still has
    open (non Won/Lost) opportunities, since that would orphan pipeline
    data the admin dashboard depends on.
    """

    @staticmethod
    def delete_customer(customer: Customer):
        from apps.opportunities.models import Opportunity

        open_opportunities = Opportunity.objects.filter(
            customer=customer
        ).exclude(stage__in=[Opportunity.Stage.WON, Opportunity.Stage.LOST])

        if open_opportunities.exists():
            raise BusinessRuleViolation(
                "This customer has open opportunities. Resolve or close them before deleting the customer."
            )

        customer.soft_delete()
