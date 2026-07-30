from django.contrib import admin

from apps.customers.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["company_name", "contact_person", "email", "status", "created_at"]
    list_filter = ["status", "industry"]
    search_fields = ["company_name", "contact_person", "email"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def get_queryset(self, request):
        return Customer.all_objects.all()
