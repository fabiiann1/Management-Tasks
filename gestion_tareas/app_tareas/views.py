from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from .models import Task
from .serializers import TaskSerializer
from rest_framework import status


class TaskViewSet(viewsets.ModelViewSet):
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  filter_backends = [
    DjangoFilterBackend,
    filters.SearchFilter,
    filters.OrderingFilter,
  ]
  filterset_fields = ["state", "due_date", "assigned_user__username"]
  search_fields = ["name", "description"]
  ordering_fields = ["due_date", "priority"]
  ordering = ['due_date']

def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', '')
        
        if ordering == 'priority':
            return queryset.order_by('priority')  # Orden alfabético ascendente
        elif ordering == '-priority':
            return queryset.order_by('-priority')  # Orden alfabético descendente
        
        return queryset

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
