from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from ..models import Task

class TaskViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        Token.objects.filter(user=self.user).delete()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.task = Task.objects.create(
            name='Tarea de prueba',
            description='Descripción de prueba',
            state='TO DO',
            priority='MEDIA',
            due_date='2023-12-31',
            assigned_user=self.user
        )

    def test_list_tasks(self):
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Tarea de prueba')

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
            'state': 'TO DO',
            'priority': 'ALTA',
            'due_date': '2023-12-31',
            'assigned_user': self.user.pk
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_filter_tasks(self):
        test_cases = [
            ('state=TO DO', 1),
            (f'assigned_user__username={self.user.username}', 1),
            ('due_date=2023-12-31', 1),
            ('state=DONE', 0)
        ]
        
        base_url = reverse('task-list')
        for query, expected_count in test_cases:
            with self.subTest(query=query):
                url = f"{base_url}?{query}"
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), expected_count)

    def test_search_ordering(self):
        # Crear tareas adicionales para pruebas
        task_high = Task.objects.create(
            name='Tarea alta prioridad',
            description='Descripción diferente',
            state='TO DO',
            priority='ALTA',
            due_date='2023-12-15',
            assigned_user=self.user
        )
        
        task_low = Task.objects.create(
            name='Tarea baja prioridad',
            description='Otra descripción',
            state='TO DO',
            priority='BAJA',
            due_date='2023-12-01',
            assigned_user=self.user
        )
        
        base_url = reverse('task-list')
        
        # Pruebas de búsqueda
        search_cases = [
            ('search=prueba', 1),
            ('search=diferente', 1),
            ('search=inexistente', 0)
        ]
        
        for query, expected_count in search_cases:
            with self.subTest(query=query):
                url = f"{base_url}?{query}"
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), expected_count)
        
        # Pruebas de ordenamiento mejoradas
        ordering_cases = [
            ('ordering=priority', ['ALTA', 'BAJA', 'MEDIA']),  # Orden alfabético
            ('ordering=-priority', ['MEDIA', 'BAJA', 'ALTA'])  # Orden inverso
        ]
        
        for query, expected_order in ordering_cases:
            with self.subTest(query=query):
                url = f"{base_url}?{query}"
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                # Verificar el orden de prioridades
                priorities = [item['priority'] for item in response.data]
                self.assertEqual(priorities, expected_order)

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
        
        # Debug: Imprimir respuesta si falla
        if response.status_code != status.HTTP_201_CREATED:
            print("Error en registro:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['username'], 'newtestuser')

    def test_login_user(self):
        # Crear usuario primero (sin token)
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
        self.assertEqual(response.data['username'], 'testloginuser')

    def test_protected_access(self):
        user = User.objects.create_user(
            username='protecteduser',
            password='testpass123',
            email='protected@example.com'
        )
        token, _ = Token.objects.get_or_create(user=user)
        
        # Sin token - debería fallar
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Con token - debería funcionar
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def tearDown(self):
        self.cleanup()
        Task.objects.all().delete()