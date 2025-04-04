from django.test import SimpleTestCase
from django.urls import reverse, resolve
from app_tareas.views import TaskViewSet, RegisterView, CustomAuthToken

class TestUrls(SimpleTestCase):
    def test_task_list_url_resolves(self):
        url = reverse('task-list')
        self.assertEqual(resolve(url).func.cls, TaskViewSet)

    def test_task_detail_url_resolves(self):
        url = reverse('task-detail', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func.cls, TaskViewSet)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, RegisterView)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, CustomAuthToken)

    def test_url_patterns(self):
        # Verifica que todas las URLs esperadas están presentes
        # Añadimos el prefijo '/api/' que parece estar en tu configuración
        url_patterns = [
            ('task-list', '/api/tasks/'),
            ('task-detail', '/api/tasks/1/'),
            ('register', '/api/register/'),
            ('login', '/api/login/'),
        ]
        
        for name, expected_path in url_patterns:
            with self.subTest(name=name, path=expected_path):
                reversed_path = reverse(name, kwargs={'pk': 1} if 'detail' in name else {})
                self.assertEqual(reversed_path, expected_path)