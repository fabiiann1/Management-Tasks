from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["id", "username"]


class TaskSerializer(serializers.ModelSerializer):
  assigned_user = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(), required=False, allow_null=True
  )

  class Meta:
    model = Task
    fields = "__all__"

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


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password2'
        )
        extra_kwargs = {
            'username': {
                'validators': [UniqueValidator(queryset=User.objects.all())]
            }
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        return user