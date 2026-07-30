from django.contrib import admin

from apps.leads.models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["company_name", "contact_name", "status", "priority", "assigned_rep", "created_at"]
    list_filter = ["status", "priority"]
    search_fields = ["company_name", "contact_name", "email"]
    readonly_fields = ["id", "created_at", "updated_at"]
