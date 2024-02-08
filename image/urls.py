from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, ImageSyncView, ImageSaveView, ImagePushView

# router = DefaultRouter()
# router.register(r'image', ImageViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('sync/', ImageSyncView.as_view(), name='image_sync'),
    path('save/', ImageSaveView.as_view(), name='image_save'),
    path('push/', ImagePushView.as_view(), name='image_push'),
    path('', ImageViewSet.as_view({'get': 'list','post': 'create',}), name='image'),
]
# urlpatterns = [
#     path('register/', UserCreateView.as_view(), name='register'),
#     path('login/', UserLoginView.as_view(), name='login'),
#     path('logout/', UserLogoutView.as_view(), name='logout')
# ]