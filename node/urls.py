from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import NodeView

# router = DefaultRouter()
# router.register(r'node', NodeView)  # get

urlpatterns = [
    # path('', include(router.urls)),
    path('', NodeView.as_view(), name='node_get'),
]