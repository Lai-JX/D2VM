import datetime
import re
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password

from .models import User, VerifyCode
import hashlib

def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


# 注册前发送验证码之前的检验
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
         # 邮箱是否注册
        if User.objects.filter(email = email).count():
            raise serializers.ValidationError('该邮箱已经注册')

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
# 注册时的校验
class UserRegisterSerializer(serializers.ModelSerializer):
    # error_message:自定义错误消息提示的格式
    code = serializers.CharField(required=True, allow_blank=False, min_length=6, max_length=6, help_text='验证码',
                                 error_messages={
                                     'blank': '请输入验证码',
                                     'required': '请输入验证码',
                                     'min_length': '验证码格式错误',
                                     'max_length': '验证码格式错误',
                                 }, write_only=True)

    # 利用drf中的validators验证username是否唯一
    username = serializers.CharField(required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message='用户已经存在')])

    email = serializers.EmailField(required=True, allow_blank=False,
                                   validators=[UniqueValidator(queryset=User.objects.all(), message='邮箱已被注册')])

    # 对code字段单独验证(validate_+字段名)
    def validate_code(self, code):
        verify_records = VerifyCode.objects.filter(email=self.initial_data['email']).order_by('-add_time')
        if verify_records:
            last_record = verify_records[0]
            # 判断验证码是否过期
            five_minutes_ago = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=5, seconds=0)  # 获取5分钟之前的时间
            if last_record.add_time < five_minutes_ago:
                raise serializers.ValidationError('验证码过期')
            # 判断验证码是否正确
            if last_record.code != code:
                raise serializers.ValidationError('验证码错误')
            # 不用将code返回到数据库中，只是做验证
            # return code
        else:
            raise serializers.ValidationError('验证码不存在')

    # attrs：每个字段validate之后总的dict
    def validate(self, attrs):
        # attrs['mobile'] = attrs['username']
        # 从attrs中删除code字段
        del attrs['code']
        return attrs

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'code')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

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
class ChangePasswdSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False,)
    old_password = serializers.CharField(max_length=128,required=True, allow_blank=False,)
    new_password = serializers.CharField(max_length=128,required=True, allow_blank=False,)#check_password

    def validate_username(self, username):
        if User.objects.filter(username=username).count():
            return username
        else:
            raise serializers.ValidationError('用户名不存在')
        

# 重置密码前发送验证码之前的检验
class ResetVerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    def validate_email(self, email):

         # 邮箱是否注册
        if User.objects.filter(email = email).count() == 0:
            raise serializers.ValidationError('该邮箱不存在')

        # 验证码发送频率
        one_minute_age = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=1, seconds=0)

        if VerifyCode.objects.filter(add_time__gt=one_minute_age, email=email).count():
            raise serializers.ValidationError({"message":'请一分钟后再次发送'})
        return email
    def validate_username(self, username):
        # 用户是否注册
        if User.objects.filter(username = username).count() == 0:
            raise serializers.ValidationError({"message":'该用户不存在'})
        return username
    
# 重置密码时的校验
class UserResetPwdSerializer(serializers.ModelSerializer):
    # error_message:自定义错误消息提示的格式
    code = serializers.CharField(required=True, allow_blank=False, min_length=6, max_length=6, help_text='验证码',
                                 error_messages={
                                     'blank': '请输入验证码',
                                     'required': '请输入验证码',
                                     'min_length': '验证码格式错误',
                                     'max_length': '验证码格式错误',
                                 }, write_only=True)
    username = serializers.CharField(required=True, allow_blank=False)

    email = serializers.EmailField(required=True, allow_blank=False)

    # 对code字段单独验证(validate_+字段名)
    def validate_code(self, code):
        verify_records = VerifyCode.objects.filter(email=self.initial_data['email']).order_by('-add_time')
        if verify_records:
            last_record = verify_records[0]
            # 判断验证码是否过期
            five_minutes_ago = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=5, seconds=0)  # 获取5分钟之前的时间
            if last_record.add_time < five_minutes_ago:
                raise serializers.ValidationError('验证码过期')
            # 判断验证码是否正确
            if last_record.code != code:
                raise serializers.ValidationError('验证码错误')
            # 不用将code返回到数据库中，只是做验证
            # return code
        else:
            raise serializers.ValidationError('验证码不存在')
    def validate_email(self, email):

         # 邮箱是否注册
        if User.objects.filter(email = email).count() == 0:
            raise serializers.ValidationError('该邮箱不存在')
        return email
    def validate_username(self, username):
        print('validate_username', username)
        # 用户是否注册
        if User.objects.filter(username = username).count() == 0:
            raise serializers.ValidationError({"message":'该用户不存在'})
        return username

    # attrs：每个字段validate之后总的dict
    def validate(self, attrs):
        # attrs['mobile'] = attrs['username']
        # 从attrs中删除code字段
        del attrs['code']
        return attrs
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'code')
        extra_kwargs = {'password': {'write_only': True}}
    

