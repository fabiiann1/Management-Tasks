from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from ..models import Task
from ..serializers import UserSerializer, TaskSerializer, RegisterSerializer
from django.core.exceptions import ValidationError as DjangoValidationError

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
        self.user = User.objects.create_user(
            username='taskuser',
            password='testpass123',
            email='task@example.com'
        )
        self.task_data = {
            'name': 'Tarea de prueba',
            'description': 'Descripción de prueba',
            'state': 'TO DO',
            'priority': 'MEDIA',
            'due_date': '2023-12-31',
            'assigned_user': self.user.id
        }

    def test_valid_task_serializer(self):
        serializer = TaskSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.name, 'Tarea de prueba')
        self.assertEqual(task.assigned_user, self.user)

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

    def test_task_serializer_update(self):
        task = Task.objects.create(
            name='Tarea original',
            description='Descripción original',
            state='BACKLOG',
            priority='BAJA',
            due_date='2023-12-01'
        )
        serializer = TaskSerializer(instance=task, data=self.task_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        self.assertEqual(updated_task.name, 'Tarea de prueba')


class RegisterSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }

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