from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from ..models import Task, State, Priority, Log
from datetime import date

class TaskViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.state = State.objects.create(code='TODO', name='To Do')
        self.priority = Priority.objects.create(code='HIGH', name='High')
        
        Token.objects.filter(user=self.user).delete()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.task = Task.objects.create(
            name='Tarea de prueba',
            description='Descripción de prueba',
            state=self.state,
            priority=self.priority,
            due_date=date(2025, 12, 31),
            assigned_user=self.user
        )

    def test_list_tasks(self):
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Tarea de prueba')

    def test_retrieve_task(self):
        url = reverse('task-detail', kwargs={'pk': self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Tarea de prueba')

    def test_create_task(self):
        url = reverse('task-list')
        data = {
            'name': 'Nueva tarea',
            'description': 'Nueva descripción',
            'state': self.state.id,
            'priority': self.priority.id,
            'due_date': '2025-12-31',
            'assigned_user': self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_filter_tasks(self):
        test_cases = [
            (f'state={self.state.id}', 1),
            (f'assigned_user__username={self.user.username}', 1),
            ('due_date=2025-12-31', 1),
            ('state=999', 0)
        ]
        
        base_url = reverse('task-list')
        for query, expected_count in test_cases:
            with self.subTest(query=query):
                url = f"{base_url}?{query}"
                response = self.client.get(url)
                if query == 'state=999':
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                else:
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    results = response.data if isinstance(response.data, list) else response.data.get('results', [])
                    self.assertEqual(len(results), expected_count)

    def test_search_ordering(self):
        # Crear estados y prioridades adicionales
        state_doing = State.objects.create(code='DOING', name='Doing')
        priority_medium = Priority.objects.create(code='MEDIUM', name='Medium')
        priority_low = Priority.objects.create(code='LOW', name='Low')
        
        # Eliminar la tarea inicial para evitar duplicados
        Task.objects.all().delete()
        
        # Crear exactamente 3 tareas para pruebas (una de cada prioridad)
        Task.objects.create(
            name='Tarea alta prioridad',
            description='Descripción diferente',
            state=state_doing,
            priority=self.priority,
            due_date=date(2025, 12, 15),
            assigned_user=self.user
        )
        
        Task.objects.create(
            name='Tarea baja prioridad',
            description='Otra descripción',
            state=self.state,
            priority=priority_low,
            due_date=date(2025, 12, 1),
            assigned_user=self.user
        )
        
        Task.objects.create(
            name='Tarea media prioridad',
            description='Descripción media',
            state=self.state,
            priority=priority_medium,
            due_date=date(2025, 12, 10),
            assigned_user=self.user
        )
        
        base_url = reverse('task-list')
        
        # Pruebas de ordenamiento
        ordering_cases = [
            ('ordering=priority', ['HIGH', 'MEDIUM', 'LOW']),
            ('ordering=-priority', ['LOW', 'MEDIUM', 'HIGH'])
        ]
        
        for query, expected_order in ordering_cases:
            with self.subTest(query=query):
                url = f"{base_url}?{query}"
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                results = response.data if isinstance(response.data, list) else response.data.get('results', [])
                priorities = [item['priority'] for item in results]
                priority_codes = [Priority.objects.get(id=p).code for p in priorities]
                self.assertEqual(priority_codes, expected_order)

    def tearDown(self):
        Task.objects.all().delete()
        Token.objects.filter(user=self.user).delete()
        self.user.delete()
#Here class log

class LogTextFormatAPIViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuserlogs',
            password='testpass123',
            email='logs@example.com'
        )
        self.state = State.objects.create(code='TODO', name='To Do')
        self.priority = Priority.objects.create(code='HIGH', name='High')
        
        Token.objects.filter(user=self.user).delete()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Limpiar completamente la base de datos antes de cada test
        Log.objects.all().delete()
        Task.objects.all().delete()
        
        self.task = Task.objects.create(
            name='Tarea para logs',
            description='Descripción',
            state=self.state,
            priority=self.priority,
            due_date=date(2025, 12, 31),
            assigned_user=self.user
        )

    def test_get_logs_authenticated(self):
        # Limpiar logs existentes
        Log.objects.all().delete()
        
        # Crear exactamente 2 logs para este test
        log1 = Log.objects.create(
            user=self.user,
            task=self.task,
            data={'state': 'TODO'}
        )
        log2 = Log.objects.create(
            user=self.user,
            task=self.task,
            data={'state': 'DOING'}
        )
        
        url = reverse('log-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que solo hay 2 logs
        self.assertEqual(len(response.data), 2)
        
        # Verificar el formato de los logs (ajustado al formato real)
        log1_str = f"{self.task.id}, {self.user.id}, {log1.created_date}, {{TODO}}"
        log2_str = f"{self.task.id}, {self.user.id}, {log2.created_date}, {{DOING}}"
        
        response_logs = [str(log) for log in response.data]
        self.assertIn(log1_str, response_logs)
        self.assertIn(log2_str, response_logs)

    def test_get_logs_unauthenticated(self):
        self.client.credentials()  # Eliminar autenticación
        url = reverse('log-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_log_format_with_missing_state(self):
        # Limpiar logs existentes
        Log.objects.all().delete()
        
        # Crear 2 logs con estado
        Log.objects.create(
            user=self.user,
            task=self.task,
            data={'state': 'TODO'}
        )
        Log.objects.create(
            user=self.user,
            task=self.task,
            data={'state': 'DOING'}
        )
        
        # Crear 1 log sin estado
        new_log = Log.objects.create(
            user=self.user,
            task=self.task,
            data={'action': 'deleted'}
        )
        
        url = reverse('log-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que hay 3 logs
        self.assertEqual(len(response.data), 3)
        
        # Verificar el log sin estado (ajustado al formato real)
        expected_log = f"{self.task.id}, {self.user.id}, {new_log.created_date}, {{}}"
        response_logs = [str(log) for log in response.data]
        self.assertIn(expected_log, response_logs)

    def tearDown(self):
        Log.objects.all().delete()
        Task.objects.all().delete()
        Token.objects.filter(user=self.user).delete()
        self.user.delete()


class AuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'newtestuser',
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': 'newuser@example.com'
        }
        self.cleanup()

    def cleanup(self):
        User.objects.filter(username='newtestuser').delete()
        Token.objects.filter(user__username='newtestuser').delete()

    def test_register_user(self):
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_login_user(self):
        user = User.objects.create_user(
            username='testloginuser',
            password='testpass123',
            email='login@example.com'
        )
        
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'testloginuser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_protected_access(self):
        user = User.objects.create_user(
            username='protecteduser',
            password='testpass123',
            email='protected@example.com'
        )
        token, _ = Token.objects.get_or_create(user=user)
        
        # Sin token
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Con token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Endpoint de logs
        url = reverse('log-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def tearDown(self):
        self.cleanup()
        Task.objects.all().delete()
        Log.objects.all().delete()