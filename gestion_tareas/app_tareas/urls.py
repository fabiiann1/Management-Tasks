from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet
<<<<<<< HEAD
from .views import RegisterView, CustomAuthToken
=======
>>>>>>> main

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
<<<<<<< HEAD
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomAuthToken.as_view(), name='login'),

=======
    
>>>>>>> main
]