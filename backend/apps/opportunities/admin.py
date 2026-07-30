from django.contrib import admin

from apps.opportunities.models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ["customer", "assigned_rep", "stage", "estimated_value", "expected_closing_date"]
    list_filter = ["stage"]
    search_fields = ["customer__company_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
