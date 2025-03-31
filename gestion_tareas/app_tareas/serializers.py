from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        

class TaskSerializer(serializers.ModelSerializer):
    assigned_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=False,allow_null=True)

    class Meta:
        model = Task
        fields = '__all__'

    def validate_assigned_user(self, value):
        """
        Valida que el usuario asignado sea válido.
        Si no se proporciona, se asigna None.
        """
        if value is None:
            return None
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("El usuario asignado no existe.")
        return value
        
