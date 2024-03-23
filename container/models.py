from datetime import datetime
from django.db import models

from image.models import Image, Node
from user.models import User

class Container(models.Model):
    container_id = models.AutoField(primary_key=True, verbose_name='容器编号')
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    file = models.FileField(upload_to='%Y/%m/%d/', null=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='所属用户')    
    node = models.ForeignKey(Node, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='运行节点')
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='使用的镜像')
    # image = models.CharField(max_length=255)

    password = models.CharField(max_length=255, default='123456')
    cmd = models.TextField(blank=True, null=True)
    path = models.CharField(max_length=255, default='/workspace')
    num_gpu = models.IntegerField(default=0)
    gpumem = models.IntegerField(null=True)
    gpucores = models.IntegerField(null=True)
    gputype = models.CharField(max_length=20, null=True)
    cpu = models.IntegerField(default=2)
    port = models.IntegerField(null=True)
    duration = models.IntegerField(default=3600)
    memory = models.CharField(max_length=10, default='10Gi')
    # capability = models.CharField(max_length=255, blank=True, null=True)
    is_VM = models.BooleanField(default=True)
    use_master = models.BooleanField(default=False)
    test = models.BooleanField(default=False)

    job_name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    pod_name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    svc_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=25, blank=True, null=True)
    
    commit_image_name = models.CharField(max_length=255, blank=True, null=True)

    capabilities = models.JSONField(max_length=255, verbose_name='capabilities', null=True)
    shm = models.CharField(max_length=10, default='64M')
    is_committing = models.BooleanField(default=False)
    # config_file_path = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.user.username + '/' + str(self.image)
    
    def save(self, *args, **kwargs):
        # 如果 published_date 字段为空，则设置为当前日期
        # if not self.published_date:
        #     self.published_date = datetime.now().date()
        super().save(*args, **kwargs)