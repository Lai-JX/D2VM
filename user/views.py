from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from rest_framework import viewsets
from .models import User
from .serializers import UserCreateSerializer, UserLoginSerializer

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) # 使用传过来的数据实例化一个序列器   
        try:
            serializer.is_valid(raise_exception=True)       # 判断数据是否有效（是否符合序列器要求，目前pass）
        except serializers.ValidationError as e:
            # 处理验证失败的情况
            error_message = e.detail
            print(error_message)
            return Response({'status': status.HTTP_403_FORBIDDEN , 'message': error_message})
            
        serializer.save()                                   # 有效则保存
        user = serializer.instance
        Token.objects.get_or_create(user=user)
        data = {"code": 200, "msg": "成功"}

        return Response(
            data=data,
            status=status.HTTP_201_CREATED
        )
    
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        print(username, password,'authenticate')
        user = authenticate(request, username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            print('login', request.user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(generics.GenericAPIView):

    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user =  request.user

        user_token = Token.objects.get(user=user)
        user_token.delete()                         # 删除 Token

        logout(request)
        print('logout', user.username)
        return Response({'logout user': user.username}, status=status.HTTP_200_OK)
    # Redirect to a success page.

# class UserViewSet(viewsets.ModelViewSet):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()