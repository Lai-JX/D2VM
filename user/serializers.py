from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import User
import hashlib

def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

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
