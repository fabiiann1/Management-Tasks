# tasks/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Task, Log, State, Priority
from .serializers import TaskCreateSerializer
from django.contrib.auth import get_user_model


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

class TaskUpdateService:
    """
    Servicio para manejar operaciones de actualización de tareas
    """
    
    @staticmethod
    def update_task_with_save(task_id, update_data, user):
        """
        Actualiza una tarea individual usando save() con validación completa
        Args:
            task_id: ID de la tarea
            update_data: Dict con campos a actualizar (ej. {'priority_code': 'HIGH'})
            user: Usuario que realiza la acción
        Returns:
            Task: Tarea actualizada
        Raises:
            ValueError: Si hay errores de validación
        """
        try:
            task = Task.objects.get(id=task_id)
            changes = {}
            
            # Manejo especial para campos relacionales
            if 'state_code' in update_data:
                new_state = State.objects.get(code=update_data.pop('state_code'))
                if task.state != new_state:
                    changes['state'] = {'old': task.state.code, 'new': new_state.code}
                    task.state = new_state
            
            if 'priority_code' in update_data:
                new_priority = Priority.objects.get(code=update_data.pop('priority_code'))
                if task.priority != new_priority:
                    changes['priority'] = {'old': task.priority.code, 'new': new_priority.code}
                    task.priority = new_priority
            
            # Actualizar campos normales
            for field, value in update_data.items():
                if hasattr(task, field) and getattr(task, field) != value:
                    changes[field] = {'old': getattr(task, field), 'new': value}
                    setattr(task, field, value)
            
            if changes:
                task.full_clean()  # Validación completa
                task.save()
                Log.objects.create(
                    task=task,
                    user=user,
                    data={
                        'action': 'update',
                        'changes': changes
                    }
                )
            
            return task
            
        except State.DoesNotExist:
            raise ValueError("El código de estado no existe")
        except Priority.DoesNotExist:
            raise ValueError("El código de prioridad no existe")
        except ValidationError as e:
            raise ValueError(f"Error de validación: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error al actualizar tarea: {str(e)}")

    @staticmethod
    @transaction.atomic
    def bulk_update_state(task_ids, new_state_code, user):
        """
        Actualización masiva del estado para múltiples tareas
        Args:
            task_ids: Lista de IDs de tareas
            new_state_code: Código del nuevo estado
            user: Usuario que realiza la acción
        Returns:
            int: Número de tareas actualizadas
        """
        try:
            state = State.objects.get(code=new_state_code)
            tasks = Task.objects.filter(id__in=task_ids)
            
            # Obtener estados anteriores para el log
            state_changes = {
                str(task.id): task.state.code
                for task in tasks
                if task.state != state
            }
            
            updated_count = tasks.update(state=state)
            
            if updated_count > 0:
                # Crear logs solo para tareas que cambiaron
                logs = [
                    Log(
                        task_id=task_id,
                        user=user,
                        data={
                            'action': 'bulk_state_update',
                            'old_state': old_state,
                            'new_state': new_state_code
                        }
                    )
                    for task_id, old_state in state_changes.items()
                ]
                Log.objects.bulk_create(logs)
            
            return updated_count
            
        except State.DoesNotExist:
            raise ValueError(f"Estado '{new_state_code}' no encontrado")
        except Exception as e:
            raise ValueError(f"Error en actualización masiva: {str(e)}")

    @staticmethod
    @transaction.atomic
    def complex_bulk_update(task_ids, update_data, user):
        """
        Actualización masiva avanzada para múltiples campos
        Args:
            task_ids: Lista de IDs de tareas
            update_data: Dict con campos a actualizar
            user: Usuario que realiza la acción
        Returns:
            int: Número de tareas actualizadas
        """
        try:
            tasks = Task.objects.filter(id__in=task_ids)
            if not tasks.exists():
                return 0
                
            # Procesar campos relacionales primero
            update_fields = list(update_data.keys())
            state = priority = None
            
            if 'state_code' in update_data:
                state = State.objects.get(code=update_data.pop('state_code'))
                update_fields.remove('state_code')
            
            if 'priority_code' in update_data:
                priority = Priority.objects.get(code=update_data.pop('priority_code'))
                update_fields.remove('priority_code')
            
            # Aplicar cambios
            for task in tasks:
                if state is not None:
                    task.state = state
                if priority is not None:
                    task.priority = priority
                for field in update_fields:
                    setattr(task, field, update_data[field])
            
            # Ejecutar actualización masiva
            Task.objects.bulk_update(
                tasks,
                update_fields + (['state'] if state else []) + (['priority'] if priority else [])
            )
            
            # Crear logs
            logs = [
                Log(
                    task=task,
                    user=user,
                    data={
                        'action': 'complex_bulk_update',
                        'changes': update_data
                    }
                )
                for task in tasks
            ]
            Log.objects.bulk_create(logs)
            
            return len(tasks)
            
        except Exception as e:
            raise ValueError(f"Error en actualización compleja: {str(e)}")
