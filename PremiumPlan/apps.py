from django.apps import AppConfig


class PremiumplanConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "PremiumPlan"

    def ready(self):
        import PremiumPlan.signals
