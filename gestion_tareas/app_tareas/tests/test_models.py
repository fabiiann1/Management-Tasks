from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Task
from datetime import date, timedelta

class TaskModelTests(TestCase):
    def setUp(self):
        # Usuario para pruebas
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Tarea de prueba
        self.task = Task.objects.create(
            name='Implementar tests',
            description='Desarrollar pruebas unitarias para la app',
            state=Task.StateChoices.TO_DO,
            priority=Task.PriorityChoices.HIGH,
            due_date=date.today() + timedelta(days=7),
            assigned_user=self.user
        )

    def test_task_creation(self):
        """Verifica la creación correcta de una tarea"""
        self.assertEqual(self.task.name, 'Implementar tests')
        self.assertEqual(self.task.state, 'TO DO')
        self.assertEqual(self.task.priority, 'ALTA')
        self.assertEqual(self.task.assigned_user, self.user)
        self.assertTrue(isinstance(self.task, Task))

    def test_state_choices(self):
        """Verifica las opciones de estado"""
        choices = Task.StateChoices
        self.assertEqual(choices.BACKLOG, 'BACKLOG')
        self.assertEqual(choices.TO_DO, 'TO DO')
        self.assertEqual(choices.DOING, 'DOING')
        self.assertEqual(choices.TEST, 'TEST')
        self.assertEqual(choices.DONE, 'DONE')

    def test_priority_choices(self):
        """Verifica las opciones de prioridad"""
        choices = Task.PriorityChoices
        self.assertEqual(choices.HIGH, 'ALTA')
        self.assertEqual(choices.MEDIUM, 'MEDIA')
        self.assertEqual(choices.LOW, 'BAJA')

    def test_default_values(self):
        """Verifica los valores por defecto"""
        default_task = Task.objects.create(
            name='Tarea con defaults',
            description='Descripción',
            due_date=date.today()
        )
        self.assertEqual(default_task.state, 'BACKLOG')
        self.assertEqual(default_task.priority, 'MEDIA')
        self.assertIsNone(default_task.assigned_user)
        self.assertIsNone(default_task.comment)

    def test_verbose_names(self):
        """Verifica los nombres legibles"""
        field_verbose_names = {
            'name': 'Nombre de la tarea',
            'description': 'Descripción de la tarea',
            'state': 'Estado',
            'priority': 'Prioridad',
            'due_date': 'Fecha de entrega',
            'comment': 'Comentario',
            'assigned_user': 'Usuario asignado',
            'created_at': 'Fecha de creación',
            'updated_at': 'Fecha de actualización'
        }
        
        for field, verbose_name in field_verbose_names.items():
            self.assertEqual(
                Task._meta.get_field(field).verbose_name,
                verbose_name
            )

    def test_meta_options(self):
        """Verifica las opciones Meta del modelo"""
        self.assertEqual(Task._meta.ordering, ['due_date', 'priority'])
        self.assertEqual(Task._meta.verbose_name, 'Tarea')
        self.assertEqual(Task._meta.verbose_name_plural, 'Tareas')

    def test_str_representation(self):
        """Verifica la representación en string"""
        self.assertEqual(str(self.task), 'Implementar tests')

    def test_comment_blank_null(self):
        """Verifica que comment puede ser blank y null"""
        task_without_comment = Task.objects.create(
            name='Tarea sin comentario',
            description='Descripción',
            due_date=date.today()
        )
        self.assertIsNone(task_without_comment.comment)

    def test_assigned_user_optional(self):
        """Verifica que assigned_user es opcional"""
        task_without_user = Task.objects.create(
            name='Tarea sin usuario',
            description='Descripción',
            due_date=date.today()
        )
        self.assertIsNone(task_without_user.assigned_user)

    def test_dates_auto_populated(self):
        """Verifica que las fechas se autocompletan correctamente"""
        new_task = Task.objects.create(
            name='Tarea con fechas',
            description='Descripción',
            due_date=date.today()
        )
        self.assertIsNotNone(new_task.created_at)
        self.assertIsNotNone(new_task.updated_at)
        self.assertEqual(new_task.created_at.date(), date.today())