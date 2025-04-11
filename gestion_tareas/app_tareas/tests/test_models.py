from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from ..models import Task, State, Priority, Log

class ModelTests(TestCase):
    def setUp(self):
        # Configuración común para todas las pruebas
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Crear instancias de State y Priority necesarias para Task
        self.state = State.objects.create(code='TODO', name='To Do')
        self.priority = Priority.objects.create(code='HIGH', name='High')
        
        # Tarea de prueba
        self.task = Task.objects.create(
            name='Implementar tests',
            description='Desarrollar pruebas unitarias para la app',
            state=self.state,
            priority=self.priority,
            due_date=date.today() + timedelta(days=7),
            assigned_user=self.user
        )

class StateModelTests(ModelTests):
    def test_state_creation(self):
        """Verifica la creación correcta de un estado"""
        state = State.objects.create(code='DONE', name='Done')
        self.assertEqual(state.code, 'DONE')
        self.assertEqual(state.name, 'Done')
        self.assertEqual(str(state), 'DONE!')  # Probando __str__
    
    def test_state_unique_code(self):
        """Verifica que el código de estado sea único"""
        with self.assertRaises(Exception):  # Puede ser IntegrityError
            State.objects.create(code='TODO', name='Duplicate')

class PriorityModelTests(ModelTests):
    def test_priority_creation(self):
        """Verifica la creación correcta de una prioridad"""
        priority = Priority.objects.create(code='LOW', name='Low')
        self.assertEqual(priority.code, 'LOW')
        self.assertEqual(priority.name, 'Low')
        self.assertEqual(str(priority), 'LOW')  # Probando __str__
    
    def test_priority_unique_code(self):
        """Verifica que el código de prioridad sea único"""
        with self.assertRaises(Exception):  # Puede ser IntegrityError
            Priority.objects.create(code='HIGH', name='Duplicate')

class TaskModelTests(ModelTests):
    def test_task_creation(self):
        """Verifica la creación correcta de una tarea"""
        self.assertEqual(self.task.name, 'Implementar tests')
        self.assertEqual(self.task.state, self.state)
        self.assertEqual(self.task.priority, self.priority)
        self.assertEqual(self.task.assigned_user, self.user)
        self.assertTrue(isinstance(self.task, Task))

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
            due_date=date.today(),
            state=self.state,
            priority=self.priority
        )
        self.assertIsNone(task_without_comment.comment)

    def test_assigned_user_optional(self):
        """Verifica que assigned_user es opcional"""
        task_without_user = Task.objects.create(
            name='Tarea sin usuario',
            description='Descripción',
            due_date=date.today(),
            state=self.state,
            priority=self.priority
        )
        self.assertIsNone(task_without_user.assigned_user)

    def test_dates_auto_populated(self):
        """Verifica que las fechas se autocompletan correctamente"""
        new_task = Task.objects.create(
            name='Tarea con fechas',
            description='Descripción',
            due_date=date.today(),
            state=self.state,
            priority=self.priority
        )
        self.assertIsNotNone(new_task.created_at)
        self.assertIsNotNone(new_task.updated_at)
        self.assertEqual(new_task.created_at.date(), date.today())

    def test_state_priority_nullable(self):
        """Verifica que state y priority pueden ser nulos"""
        task = Task.objects.create(
            name='Tarea sin estado ni prioridad',
            description='Descripción',
            due_date=date.today()
        )
        self.assertIsNone(task.state)
        self.assertIsNone(task.priority)

class LogModelTests(ModelTests):
    def test_log_creation(self):
        """Verifica la creación correcta de un log"""
        log_data = {'action': 'created', 'details': 'task was created'}
        log = Log.objects.create(
            user=self.user,
            task=self.task,
            data=log_data
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.task, self.task)
        self.assertEqual(log.data, log_data)
        self.assertEqual(log.created_date, date.today())
        self.assertTrue(isinstance(log, Log))
    
    def test_log_str_representation(self):
        """Verifica la representación en string del log"""
        log_data = {'state': 'TODO', 'action': 'update'}
        log = Log.objects.create(
            user=self.user,
            task=self.task,
            data=log_data
        )
        expected_str = f"{self.task.id}, {self.user.id}, {date.today()}, {{'TODO'}}"
        self.assertEqual(str(log), expected_str)
    
    def test_log_required_fields(self):
        """Verifica que los campos requeridos son obligatorios"""
        with self.assertRaises(Exception):
            Log.objects.create()  # Sin campos requeridos
        
        with self.assertRaises(Exception):
            Log.objects.create(
                user=self.user,
                task=self.task
            )  # Falta data
        
        with self.assertRaises(Exception):
            Log.objects.create(
                user=self.user,
                data={}
            )  # Falta task
        
        with self.assertRaises(Exception):
            Log.objects.create(
                task=self.task,
                data={}
            )  # Falta user