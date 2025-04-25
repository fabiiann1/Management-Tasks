from rest_framework import viewsets, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from .models import Task, Log
from .serializers import TaskSerializer
from rest_framework import status
from .services import TaskCreationService, TaskUpdateService

class TaskViewSet(viewsets.ModelViewSet):
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  filter_backends = [
    DjangoFilterBackend,
    filters.SearchFilter,
    filters.OrderingFilter,
  ]
  filterset_fields = ["state", "due_date", "assigned_user__id"]
  search_fields = ["name", "description"]
  ordering_fields = ["due_date", "priority"]
  ordering = ['due_date']

def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', '')
        
        if ordering == 'priority':
            return queryset.order_by('priority')  
        elif ordering == '-priority':
            return queryset.order_by('-priority')  
        
        return queryset

class TaskCreateAPIView(APIView):
    #Endpoint para creación individual de tareas
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            task_data = request.data
            
            task = TaskCreationService.create_task_with_save(task_data, user)
            serializer = TaskSerializer(task)
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class BulkTaskCreateAPIView(APIView):
    #Endpoint para creación masiva de tareas
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            tasks_data = request.data.get('tasks', [])
            
            count = TaskCreationService.bulk_create_tasks(tasks_data, user)
            
            return Response({
                'count': count,
                'status': 'bulk_created'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class TaskUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self,request,pk):
        try:
            task = TaskUpdateService.update_task_with_save(
                task_id=pk,
                update_data=request.data,
                user=request.user
            )
            serializer = TaskSerializer(task)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class BulkTaskStateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if not isinstance(request.data.get('task_ids',None), list):
                raise ValueError("Se requiere una lista de Ids en 'task_ids'")
            
            update_count = TaskUpdateService.bulk_update_state(
                task_ids=request.data['task_ids'],
                new_state_code=request.data['state_code'],
                user=request.user
            )
            return Response({
                'update_count':update_count,
                'status': 'bulk_state_updated'
            })
        except Exception as e:
            return Response (
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class BulkTaskUpdateAPIView(APIView):
    permission_classes=[IsAuthenticated]
    
    def post(self,request):
        try:
            if not isinstance(request.data.get('task_ids', None),list):
                raise ValueError("Se requiere una lista de IDs en 'task_ids'")
            update_count = TaskUpdateService.complex_bulk_update(
            task_ids=request.data['tasks_ids'],
            update_data=request.data['update_data'],
            user=request.user
        )
            return Response({
            'update_count': update_count,
            'status':'bulk_updated'
        })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogTextFormatAPIView(APIView):
    permission_classes = [IsAuthenticated]  
    
    def get(self, request):
        logs = Log.objects.select_related('user', 'task').order_by('created_date')
        data = []

        for log in logs:
            estado = log.data.get('state', '') 
            line = f"{log.task.id}, {log.user.id}, {log.created_date}, {{{estado}}}"
            data.append(line)

        return Response(data)
    
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'token': token.key,
                'user_id': user.pk,
                'username': user.username
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class CustomAuthToken(ObtainAuthToken):
  def post(self, request, *args, **kwargs):
    serializer = self.serializer_class(
      data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    token, created = Token.objects.get_or_create(user=user)
    return Response(
      {"token": token.key, "user_id": user.id, "username": user.username}
    )

  ordering_fields = ["due_date", "priority"]


