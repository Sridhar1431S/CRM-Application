import uuid

from django.db import models


class CustomerQuerySet(models.QuerySet):
    def alive(self):
        """Excludes soft-deleted rows. Used as the default manager queryset."""
        return self.filter(deleted_at__isnull=True)


class CustomerManager(models.Manager):
    def get_queryset(self):
        return CustomerQuerySet(self.model, using=self._db).alive()


class AllCustomersManager(models.Manager):
    """Unfiltered manager (includes soft-deleted rows) for admin/reporting use."""

    def get_queryset(self):
        return CustomerQuerySet(self.model, using=self._db)


class Customer(models.Model):
    class Status(models.TextChoices):
        PROSPECT = "prospect", "Prospect"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company_name = models.CharField(max_length=255, db_index=True)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20)
    industry = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PROSPECT, db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = CustomerManager()
    all_objects = AllCustomersManager()

    class Meta:
        db_table = "customers"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["company_name"]),
        ]

    def __str__(self):
        return self.company_name

    def soft_delete(self):
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])
