from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserCreateView, UserLoginView, UserLogoutView, VerifyCodeView

# router = DefaultRouter()
# router.register(r'user', UserViewSet)

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('register/sendCode/', VerifyCodeView.as_view(), name='sendCode'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout')
]