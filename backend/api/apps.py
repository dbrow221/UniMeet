from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
<<<<<<< HEAD

    def ready(self):
        import api.signals
=======
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e
