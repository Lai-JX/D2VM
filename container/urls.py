from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ContainerView, ContainerGetView, ContainerDockerRestartView, ContainerDeleteServiceView

# router = DefaultRouter()
# router.register(r'container', ContainerViewSet, basename='container')

urlpatterns = [
    # path('', include(router.urls)),
    path('get/', ContainerGetView.as_view(), name='container_get'),
    path('dockerRestart/', ContainerDockerRestartView.as_view(), name='docker_restart'),
    path('deleteService/', ContainerDeleteServiceView.as_view(), name='deleteService'),
    path('', ContainerView.as_view({'post': 'create','delete': 'delete',}), name='container'),
]