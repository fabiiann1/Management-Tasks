from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet
from .views import RegisterView, CustomAuthToken

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = [
  path("", include(router.urls)),
  path("register/", RegisterView.as_view(), name="register"),
  path("login/", CustomAuthToken.as_view(), name="login"),
  

]
