from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ContainerCreateView

# router = DefaultRouter()
# router.register(r'container', ContainerViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('create/', ContainerCreateView.as_view(), name='register'),
]