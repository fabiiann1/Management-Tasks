from rest_framework import serializers
from .models import Task
from .models import State
from .models import Priority
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
    
class TaskCreateSerializer(serializers.ModelSerializer):
    state_code = serializers.CharField(write_only=True)
    priority_code = serializers.CharField(write_only=True)
    assigned_user_username = serializers.CharField(
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Task
        fields = [
            'name',
            'description',
            'state_code',
            'priority_code',
            'due_date',
            'comment',
            'assigned_user_username'
        ]
        extra_kwargs = {
            'comment': {'required': False, 'allow_blank': True},
            'due_date': {'required': True}
        }

    def validate_state_code(self, value):
        if not State.objects.filter(code=value).exists():
            raise serializers.ValidationError("El código de estado no existe.")
        return value

    def validate_priority_code(self, value):
        if not Priority.objects.filter(code=value).exists():
            raise serializers.ValidationError("El código de prioridad no existe.")
        return value

    def validate_assigned_user_username(self, value):
        if value is None or value == '':
            return None
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario asignado no existe.")
        return value

    def create(self, validated_data):
        # Extraemos los campos especiales
        state_code = validated_data.pop('state_code')
        priority_code = validated_data.pop('priority_code')
        username = validated_data.pop('assigned_user_username', None)
        
        # Obtenemos las instancias relacionadas
        state = State.objects.get(code=state_code)
        priority = Priority.objects.get(code=priority_code)
        assigned_user = User.objects.get(username=username) if username else None
        
        # Creamos la tarea
        task = Task.objects.create(
            **validated_data,
            state=state,
            priority=priority,
            assigned_user=assigned_user
        )
        
        return task