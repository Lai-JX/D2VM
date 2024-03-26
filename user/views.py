from random import choice
from django.shortcuts import render
from D2VM import settings
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail

# Create your views here.
from rest_framework import viewsets
from .models import User, VerifyCode
from .serializers import ChangePasswdSerializer, ResetVerifyCodeSerializer, UserCreateSerializer, UserLoginSerializer, UserRegisterSerializer, UserResetPwdSerializer, VerifyCodeSerializer
def generate_code():
        """
        生成6位数验证码 防止破解
        :return:
        """
        seeds = "1234567890abcdefghijklmnopqrstuvwxyz"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)
def send_code_email(code, to_email_adress, send_type="register"):
    # 如果为注册类型
    if send_type == "register":
        email_title = "HAIOS 系统验码"
        # email_body = "请点击下面的链接激活你的账号:http://127.0.0.1:8000/active/{0}".format(code)
        email_body = "您的邮箱注册验证码为：{0}, 该验证码有效时间为5分钟，请及时进行验证。".format(code)
        # 发送邮件
        send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [to_email_adress])
        if not send_status:
            return False
    if send_type == "reset":
        email_title = "HAIOS 系统验码"
        email_body = "您的邮箱验证码为：{0}, 该验证码有效时间为5分钟，请及时进行验证。".format(code)
        # 发送邮件
        send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [to_email_adress])
        if not send_status:
            return False
    return True

class VerifyCodeView(generics.CreateAPIView):
    """
    发送验证码
    """
    permission_classes = [AllowAny] #允许所有人注册
    serializer_class = VerifyCodeSerializer #相关的发送前验证逻辑

    def create(self, request, *args, **kwargs):
        print("/user/register/sendCode")
        serializer = self.get_serializer(data=request.data)             # email和username
        serializer.is_valid(raise_exception=True) #这一步相当于发送前验证
        # 从 validated_data 中获取 email
        email = serializer.validated_data["email"]
        # 随机生成code
        code = generate_code()

        # 发送短信或邮件验证码
        sms_status = send_code_email(code=code, to_email_adress=email)

        if sms_status == 0:            
            return Response({"msg": "邮件发送失败"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            code_record = VerifyCode(code=code, email=email)
            # 保存验证码
            code_record.save()   
            return Response(
                {"message": f"验证码已经向 {email} 发送完成"}, status=status.HTTP_201_CREATED
            )
# 注册
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

# Deprecated
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
            return Response({'message': error_message}, status=status.HTTP_403_FORBIDDEN )
            
        serializer.save()                                   # 有效则保存
        user = serializer.instance
        Token.objects.get_or_create(user=user)

        return Response(
            {"message": "成功"},
            status=status.HTTP_201_CREATED
        )
# 登录    
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
            if not created:                             # 删除原有的token，避免多客户端登录
                token.delete()
                print("delete the token before")
                token = Token.objects.create(user=user)
            login(request, user)
            print('login', request.user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# 登出
class UserLogoutView(generics.GenericAPIView):

    # 采用token验证
    # authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user =  request.user
        try:
            user_token = Token.objects.get(user=user)
            user_token.delete()                         # 删除 Token

            logout(request)
            print('logout', user.username)
            return Response({'logout user': user.username}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_403_FORBIDDEN)
    # Redirect to a success page.

# 修改密码
class ChangePasswdView(generics.UpdateAPIView):
    serializer_class = ChangePasswdSerializer
    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)
            if user.check_password(serializer.validated_data['old_password']):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'message': '密码错误'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_403_FORBIDDEN)


class ResetVerifyCodeView(VerifyCodeView):
    """
    发送验证码
    """
    permission_classes = [AllowAny] #允许所有人注册
    serializer_class = ResetVerifyCodeSerializer #相关的发送前验证逻辑

# 重置密码
class ResetPasswdView(generics.UpdateAPIView):
    serializer_class = UserResetPwdSerializer

    def post(self, request, *args, **kwargs):
        try:
            print('ResetPasswdView')
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            print('ResetPasswdView1')
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)

            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_403_FORBIDDEN)