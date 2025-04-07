from django.conf import settings
from django.db.models.signals import post_save, pre_save
from .models import Task, Log
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  if created:
    Token.objects.create(user=instance)
    

@receiver(post_save, sender=Task)
def log_task_changes(sender, instance, created, **kwargs):
    # Determina el usuario (el asignado o un usuario por defecto)
    user = instance.assigned_user or User.objects.filter(is_staff=True).first()
    
   
    log_data = {
        'state': instance.state.code,
        'task_id': instance.id,
        'priority': instance.priority.code,
        'due_date': instance.due_date.isoformat() if instance.due_date else None
    }
    
    
    Log.objects.create(
        user=user,
        task=instance,
        data=log_data
    )
