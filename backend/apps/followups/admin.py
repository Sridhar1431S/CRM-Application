from django.contrib import admin

from apps.followups.models import FollowUp


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ["opportunity", "next_followup_date", "created_by", "created_at"]
    list_filter = ["next_followup_date"]
    readonly_fields = ["id", "created_at"]
