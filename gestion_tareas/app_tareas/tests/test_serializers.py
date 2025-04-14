from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from ..models import Task, State, Priority
from ..serializers import UserSerializer, TaskSerializer, RegisterSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import date

class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.serializer = UserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {'id', 'username'})

    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['id'], self.user.id)


class TaskSerializerTest(TestCase):
    def setUp(self):
        # Crear usuario
        self.user = User.objects.create_user(
            username='taskuser',
            password='testpass123',
            email='task@example.com'
        )
        
        # Crear State y Priority necesarios
        self.state = State.objects.create(code='TODO', name='To Do')
        self.priority = Priority.objects.create(code='HIGH', name='High')
        
        # Datos para la tarea con fechas en 2025
        self.task_data = {
            'name': 'Tarea de prueba',
            'description': 'Descripción de prueba',
            'state': self.state.id,
            'priority': self.priority.id,
            'due_date': '2025-12-31',  # Actualizado a 2025
            'assigned_user': self.user.id
        }

    def test_valid_task_serializer(self):
        serializer = TaskSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.name, 'Tarea de prueba')
        self.assertEqual(task.assigned_user, self.user)
        self.assertEqual(task.state, self.state)
        self.assertEqual(task.priority, self.priority)
        self.assertEqual(str(task.due_date), '2025-12-31')  # Verificamos la fecha

    def test_task_serializer_without_assigned_user(self):
        data = self.task_data.copy()
        data['assigned_user'] = None
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertIsNone(task.assigned_user)

    def test_task_serializer_with_invalid_user(self):
        data = self.task_data.copy()
        data['assigned_user'] = 9999  # ID que no existe
        serializer = TaskSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_task_serializer_with_invalid_state(self):
        data = self.task_data.copy()
        data['state'] = 9999  # ID que no existe
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('state', serializer.errors)

    def test_task_serializer_with_invalid_priority(self):
        data = self.task_data.copy()
        data['priority'] = 9999  # ID que no existe
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('priority', serializer.errors)

    def test_task_serializer_without_state_and_priority(self):
        data = {
            'name': 'Tarea sin estado ni prioridad',
            'description': 'Descripción',
            'due_date': '2025-06-15'  # Actualizado a 2025
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertIsNone(task.state)
        self.assertIsNone(task.priority)
        self.assertEqual(str(task.due_date), '2025-06-15')  # Verificamos la fecha

    def test_task_serializer_update(self):
        task = Task.objects.create(
            name='Tarea original',
            description='Descripción original',
            due_date='2025-01-01'  # Actualizado a 2025
        )
        serializer = TaskSerializer(instance=task, data=self.task_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        self.assertEqual(updated_task.name, 'Tarea de prueba')
        self.assertEqual(updated_task.state, self.state)
        self.assertEqual(updated_task.priority, self.priority)
        self.assertEqual(str(updated_task.due_date), '2025-12-31')  # Verificamos la fecha

    def test_read_only_fields(self):
        """Verifica que los campos de fecha son de solo lectura"""
        task = Task.objects.create(
            name='Tarea con fechas',
            description='Descripción',
            state=self.state,
            priority=self.priority,
            due_date='2025-07-01'  # Actualizado a 2025
        )
        
        # Intentar modificar campos de solo lectura con fechas en 2025
        data = {
            'created_at': '2025-01-01T00:00:00Z',
            'updated_at': '2025-01-01T00:00:00Z'
        }
        serializer = TaskSerializer(instance=task, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        
        # Los campos no deberían haber cambiado
        self.assertNotEqual(updated_task.created_at.isoformat(), '2025-01-01T00:00:00Z')
        self.assertNotEqual(updated_task.updated_at.isoformat(), '2025-01-01T00:00:00Z')


class RegisterSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }

    # Los tests de RegisterSerializer no tienen fechas, se mantienen igual
    def test_valid_registration(self):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('ComplexPass123!'))

    def test_password_mismatch(self):
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass123!'
        serializer = RegisterSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
        self.assertIn('password', serializer.errors)

    def test_weak_password(self):
        data = self.valid_data.copy()
        data['password'] = data['password2'] = '123'
        serializer = RegisterSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_unique_username(self):
        User.objects.create_user(
            username='existinguser',
            password='testpass123',
            email='existing@example.com'
        )
        data = self.valid_data.copy()
        data['username'] = 'existinguser'
        serializer = RegisterSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_unique_email(self):
        User.objects.create_user(
            username='otheruser',
            password='testpass123',
            email='existing@example.com'
        )
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        serializer = RegisterSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_required_fields(self):
        for field in ['username', 'email', 'password', 'password2']:
            data = self.valid_data.copy()
            del data[field]
            serializer = RegisterSerializer(data=data)
            with self.assertRaises(ValidationError):
                serializer.is_valid(raise_exception=True)

    def test_email_required(self):
        data = self.valid_data.copy()
        data['email'] = ''
        serializer = RegisterSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
        self.assertIn('email', serializer.errors)