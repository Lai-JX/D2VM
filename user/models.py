from django.db import models
from django.contrib.auth.models import AbstractUser # username, password and email are required. Other fields are optional.

# Create your models here.
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True, verbose_name='用户编号')
    password = models.CharField(max_length=128, null=True, verbose_name='用户密码')
    username = models.CharField(max_length=128, null=True, unique=True, verbose_name='用户姓名')
    email = models.CharField(max_length=128, null=True, verbose_name='用户邮箱')


    class Meta:
        ordering = ['user_id']
        db_table = 'user'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.username