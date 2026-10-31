from django.apps import AppConfig


class BibliotecaConfig(AppConfig):
    name = 'biblioteca'

    def ready(self):
        from biblioteca import signals  # noqa: F401
