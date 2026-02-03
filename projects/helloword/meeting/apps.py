from django.apps import AppConfig


class MeetingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meeting'
    
class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages"

    def ready(self):
        import pages.signals