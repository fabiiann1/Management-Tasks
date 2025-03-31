from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Task
from .serializers import TaskSerializer
from django_filters.rest_framework import DjangoFilterBackend

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['state', 'due_date', 'assigned_user__username']
    search_fields = ['name', 'description']
<<<<<<< HEAD
    ordering_fields = ['due_date', 'priority']
    
=======
    ordering_fields = ['due_date', 'priority']
>>>>>>> main
