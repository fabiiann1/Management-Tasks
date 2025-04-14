# tasks/services.py
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Task, Log, State, Priority
from .serializers import TaskCreateSerializer


User = get_user_model()

class TaskCreationService:
    """
    Servicio para manejar la creación de tareas con validación mejorada
    """
    
    @staticmethod
    def create_task_with_save(task_data, user):
        """
        Crea una tarea usando el método save() con validación mediante serializer
        Args:
            task_data (dict): {
                'name': str,
                'description': str,
                'state_code': str,
                'priority_code': str,
                'due_date': str (YYYY-MM-DD),
                'comment': str (opcional),
                'assigned_user_username': str (opcional)
            }
            user (User): Usuario que realiza la acción
            
        Returns:
            Task: Tarea creada
            
        Raises:
            ValueError: Si hay errores en los datos
        """
        try:
            # Si no se especifica usuario asignado, asignar al usuario actual
            if 'assigned_user_username' not in task_data or not task_data['assigned_user_username']:
                task_data['assigned_user_username'] = user.username
            
            serializer = TaskCreateSerializer(data=task_data)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            
            # Crear log inicial
            Log.objects.create(
                task=task,
                user=user,
                data={
                    'action': 'create',
                    'state': task.state.code,
                    'priority': task.priority.code
                }
            )
            
            return task
            
        except Exception as e:
            raise ValueError(f"Error creating task: {str(e)}")

    @staticmethod
    @transaction.atomic
    def bulk_create_tasks(tasks_data, user):
        """
        Crea múltiples tareas usando bulk_create() con validación
        Args:
            tasks_data (list[dict]): Lista de diccionarios con datos de tareas
            user (User): Usuario que realiza la acción
            
        Returns:
            int: Número de tareas creadas
            
        Raises:
            ValueError: Si hay errores en los datos
        """
        try:
            # Pre-validar todos los datos primero
            valid_tasks = []
            for task_data in tasks_data:
                # Asignar usuario actual si no se especifica
                if 'assigned_user_username' not in task_data or not task_data['assigned_user_username']:
                    task_data['assigned_user_username'] = user.username
                
                serializer = TaskCreateSerializer(data=task_data)
                serializer.is_valid(raise_exception=True)
                valid_tasks.append(serializer.validated_data)
            
            # Pre-cargar relaciones para mejor performance
            states = {s.code: s for s in State.objects.all()}
            priorities = {p.code: p for p in Priority.objects.all()}
            users = {u.username: u for u in User.objects.filter(
                username__in={t['assigned_user_username'] for t in valid_tasks if t['assigned_user_username']}
            )}
            
            # Preparar objetos para bulk_create
            tasks_to_create = []
            for data in valid_tasks:
                task = Task(
                    name=data['name'],
                    description=data['description'],
                    state=states[data['state_code']],
                    priority=priorities[data['priority_code']],
                    due_date=data['due_date'],
                    assigned_user=users.get(data['assigned_user_username']),
                    comment=data.get('comment', '')
                )
                tasks_to_create.append(task)
            
            # Ejecutar bulk_create
            created_tasks = Task.objects.bulk_create(tasks_to_create)
            
            # Crear logs en bulk
            logs = [
                Log(
                    task=task,
                    user=user,
                    data={
                        'action': 'bulk_create',
                        'state': task.state.code,
                        'priority': task.priority.code
                    }
                ) for task in created_tasks
            ]
            Log.objects.bulk_create(logs)
            
            return len(created_tasks)
            
        except Exception as e:
            raise ValueError(f"Error in bulk creation: {str(e)}")