from django.apps import AppConfig
from django.conf import settings


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

    def ready(self):
        if settings.SCHEDULER_DEFAULT:
            from . import scheduler

            scheduler.start()
