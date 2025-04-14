from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField


class State(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code}!"


class Priority(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code}"


class Task(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre de la tarea")
    description = models.TextField(verbose_name="Descripción de la tarea")
    state = models.ForeignKey(
      State,
      on_delete=models.SET_NULL,
      null=True,
      verbose_name="Estado")
    priority = models.ForeignKey(
      Priority,
      on_delete=models.SET_NULL,
      null=True,
      verbose_name="Prioridad")
    
    due_date = models.DateField(verbose_name="Fecha de entrega")
    comment = models.TextField(
      blank=True,
      null=True,
      verbose_name="Comentario")
    
    assigned_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name="Usuario asignado"
    )
    
    created_at = models.DateTimeField(
      auto_now_add=True,
      verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
      auto_now=True,
      verbose_name="Fecha de actualización")

    class Meta:
        ordering = ["due_date", "priority"]
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"

    def __str__(self):
        return self.name


class Log(models.Model):
    user = models.ForeignKey(
      User,
      on_delete=models.CASCADE,
      verbose_name="Usuario")
    task = models.ForeignKey(
      Task,
      on_delete=models.CASCADE,
      verbose_name="Tarea")
    created_date = models.DateField(
      auto_now_add=True,
      verbose_name="Fecha del log")
    data = JSONField(verbose_name="Datos del log") 

    def __str__(self):
        return f"{self.task.id}, {self.user.id}, {self.created_date}, {{'{self.data.get('state', '')}'}}"