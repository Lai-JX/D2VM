from django.db import models

# Create your models here.
class Image(models.Model):
    image_id = models.AutoField(primary_key=True, verbose_name='镜像编号')
    commit_date = models.DateTimeField(auto_now=True)

    registry = models.CharField(max_length=255)
    name = models.CharField(max_length=255, verbose_name='镜像名')
    tag = models.CharField(max_length=255)
    source = models.CharField(max_length=255)           # username or public
    type = models.CharField(max_length=255, null=True, blank=True)