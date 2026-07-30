from apps.users.models import User


class SalesRepService:
    @staticmethod
    def active_reps_count() -> int:
        return User.objects.filter(role=User.Role.SALES_REP, is_active=True).count()
