from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class SignalTests(TestCase):
    def test_token_created_on_user_creation(self):
        """
        Test que verifica que se crea un token automáticamente
        cuando se crea un nuevo usuario
        """
        # Verificar que no hay tokens al inicio
        self.assertEqual(Token.objects.count(), 0)
        
        # Crear un nuevo usuario
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Verificar que el usuario se creó
        self.assertEqual(User.objects.count(), 1)
        
        # Verificar que se creó exactamente un token para este usuario
        self.assertEqual(Token.objects.count(), 1)
        
        # Obtener el token creado
        token = Token.objects.first()
        
        # Verificar que el token está asociado al usuario correcto
        self.assertEqual(token.user, user)
        
    def test_no_token_created_when_user_updated(self):
        """
        Test que verifica que no se crea un token cuando
        se actualiza un usuario existente
        """
        # Crear usuario inicial
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Limpiar todos los tokens (por si acaso)
        Token.objects.all().delete()
        
        # Actualizar el usuario
        user.username = 'updateduser'
        user.save()
        
        # Verificar que no se creó ningún token nuevo
        self.assertEqual(Token.objects.count(), 0)