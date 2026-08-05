"""
Small object builders shared by the test suite.

Deliberately plain functions rather than a factory library: the models have
few required fields, and this keeps the test dependencies to what is already
in requirements.txt.
"""

from datetime import timedelta

from django.utils import timezone

from apps.customers.models import Customer
from apps.followups.models import FollowUp
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.users.models import User

_counter = {"value": 0}


def unique_suffix() -> int:
    _counter["value"] += 1
    return _counter["value"]


def create_admin(**kwargs) -> User:
    kwargs.setdefault("email", f"admin{unique_suffix()}@crmlite.test")
    kwargs.setdefault("name", "Alex Admin")
    kwargs.setdefault("password", "Admin@12345")
    kwargs["role"] = User.Role.ADMIN
    password = kwargs.pop("password")
    return User.objects.create_user(password=password, **kwargs)


def create_sales_rep(**kwargs) -> User:
    kwargs.setdefault("email", f"rep{unique_suffix()}@crmlite.test")
    kwargs.setdefault("name", "Priya Rep")
    kwargs.setdefault("password", "Rep@12345")
    kwargs["role"] = User.Role.SALES_REP
    password = kwargs.pop("password")
    return User.objects.create_user(password=password, **kwargs)


def create_customer(**kwargs) -> Customer:
    suffix = unique_suffix()
    kwargs.setdefault("company_name", f"Acme {suffix}")
    kwargs.setdefault("contact_person", f"Contact {suffix}")
    kwargs.setdefault("email", f"customer{suffix}@example.test")
    kwargs.setdefault("phone_number", "+91 9000000001")
    return Customer.objects.create(**kwargs)


def create_lead(**kwargs) -> Lead:
    suffix = unique_suffix()
    kwargs.setdefault("company_name", f"Prospect {suffix}")
    kwargs.setdefault("contact_name", f"Lead Contact {suffix}")
    kwargs.setdefault("email", f"lead{suffix}@example.test")
    kwargs.setdefault("phone_number", "+91 9111111111")
    return Lead.objects.create(**kwargs)


def create_opportunity(**kwargs) -> Opportunity:
    if "customer" not in kwargs:
        kwargs["customer"] = create_customer()
    kwargs.setdefault("estimated_value", 50000)
    kwargs.setdefault("expected_closing_date", timezone.localdate() + timedelta(days=30))
    return Opportunity.objects.create(**kwargs)


def create_followup(**kwargs) -> FollowUp:
    if "opportunity" not in kwargs:
        kwargs["opportunity"] = create_opportunity()
    kwargs.setdefault("note", "Discovery call completed.")
    return FollowUp.objects.create(**kwargs)
