from django.apps import AppConfig


class AppTareasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_tareas'

    def ready(self):
        """
        Registra las señales cuando la aplicación está lista.
        """
        import app_tareas.signals  # Importa las señales