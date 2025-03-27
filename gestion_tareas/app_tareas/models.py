from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import TextChoices

# Create your models here.
class Task(models.Model):
    class StateChoices(TextChoices):
        BACKLOG = 'BACKLOG', 'Backlog'
        TO_DO = 'TO DO', 'To Do'
        DOING = 'DOING', 'Doing'
        TEST = 'TEST', 'Test'
        DONE = 'DONE', 'Done'

    class PriorityChoices(TextChoices):
        HIGH = 'ALTA', 'Alta'
        MEDIUM = 'MEDIA', 'Media'
        LOW = 'BAJA', 'Baja'
    
    name = models.CharField(max_length=200, verbose_name="Nombre de la tarea")
    description = models.TextField(verbose_name="Descripción de la tarea")
    state = models.CharField(max_length=10,choices=StateChoices.choices,
    default=StateChoices.BACKLOG,verbose_name="Estado")
    priority = models.CharField(max_length=5,choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM,verbose_name="Prioridad")
    due_date = models.DateField(verbose_name="Fecha de entrega")
    comment = models.TextField(blank=True, null=True, verbose_name="Comentario")
    assigned_user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='assigned_tasks',verbose_name="Usuario asignado")
    
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        ordering = ['due_date', 'priority']
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
    
    def __str__(self):
        return self.name
    