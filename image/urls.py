from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, ImageSyncView, ImageSaveView, ImagePushView, ImageAddNoteView, ImageChmodView, ImageAsyncView

# router = DefaultRouter()
# router.register(r'image', ImageViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('sync/', ImageSyncView.as_view(), name='image_sync'),
    path('save/', ImageSaveView.as_view(), name='image_save'),
    path('push/', ImagePushView.as_view(), name='image_push'),
    path('addNote/', ImageAddNoteView.as_view(), name='image_add_note'),
    path('chmod/', ImageChmodView.as_view(), name='image_change_mode'),
    path('test/', ImageAsyncView.as_view()),
    path('', ImageViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'delete',}), name='image'),
]
# urlpatterns = [
#     path('register/', UserCreateView.as_view(), name='register'),
#     path('login/', UserLoginView.as_view(), name='login'),
#     path('logout/', UserLogoutView.as_view(), name='logout')
# ]