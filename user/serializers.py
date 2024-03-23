import datetime
import re
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import User, VerifyCode
import hashlib

def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

# 发送验证码之前的检验
class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    def validate_email(self, email):
        """
        验证邮箱是否合法
        """

        # 验证邮箱号码合法
        # if not re.match(EMAIL_REGEX, email):
        #     raise serializers.ValidationError('邮箱格式错误')

        # 验证码发送频率
        one_minute_age = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=1, seconds=0)
        print(one_minute_age, datetime.datetime.now(), datetime.timedelta(hours=0, minutes=1, seconds=0))
        if VerifyCode.objects.filter(add_time__gt=one_minute_age, email=email).count():
            raise serializers.ValidationError({"message":'请一分钟后再次发送'})
        return email
    def validate_username(self, username):
        # 用户是否注册
        if User.objects.filter(username = username).count():
            raise serializers.ValidationError({"message":'该用户已经注册'})
        return username


class UserCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    # 一些验证，如字段校验等
    def validate(self, attrs):
        # print(attrs)
        # attrs['password'] = hash_code(attrs['password'])
        # print(attrs)
        return attrs
    def create(self, validated_data):
        """保存用户信息"""
        username = validated_data.get("username")
        email = validated_data.get("email")

        raw_password = validated_data.get("password")
        hash_password = make_password(raw_password)
        # 调用序列化器提供的create方法
        user = User.objects.create(
            username=username,
            password=hash_password,
            email=email
        )
        return user

    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        # attrs['password'] = make_password(attrs['password'])
        return attrs
