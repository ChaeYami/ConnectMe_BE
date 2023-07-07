from django.apps import AppConfig
from django.conf import settings


class MeetingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meeting'

    def ready(self):
        import meeting.signals
        
        if settings.SCHEDULER_DEFAULT:
            from . import operator
            operator.start()