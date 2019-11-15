from django.apps import AppConfig


class WebappConfig(AppConfig):
    name = 'webapp'

    def ready(self):
        # so the decorators there will run
        from . import signals  # noqa: F401
