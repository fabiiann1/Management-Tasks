from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, LogTextFormatAPIView, RegisterView, CustomAuthToken, TaskCreateAPIView,BulkTaskCreateAPIView


router = DefaultRouter()
router.register(r"tasks", TaskViewSet,basename='task')


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logs/', LogTextFormatAPIView.as_view(), name='log-list'),
    path('tasks/create/',TaskCreateAPIView.as_view(), name='task-create'),
    path('tasks/bulk-create/',BulkTaskCreateAPIView.as_view(),name='bulk-task-create'),
    path('', include(router.urls)),

    
]