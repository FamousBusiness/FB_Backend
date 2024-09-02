from django.apps import AppConfig


class SoftwareConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Software"

    def ready(self):
        import Software.signals
        
