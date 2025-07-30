# login_activity/apps.py
from django.apps import AppConfig

class LoginActivityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login_activity'

    def ready(self):
        import login_activity.signals
