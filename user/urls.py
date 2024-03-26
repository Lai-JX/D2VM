from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ResetPasswdView, ResetVerifyCodeView, UserCreateView, UserLoginView, UserLogoutView, VerifyCodeView, UserRegisterView, ChangePasswdView

# router = DefaultRouter()
# router.register(r'user', UserViewSet)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('register/sendCode/', VerifyCodeView.as_view(), name='register_sendCode'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('changePwd/', ChangePasswdView.as_view(), name='register'),
    path('reset/', ResetPasswdView.as_view(), name='reset'),
    path('reset/sendCode/', ResetVerifyCodeView.as_view(), name='reset_sendCode'),
    path('register_test/', UserCreateView.as_view(), name='register1'),
]