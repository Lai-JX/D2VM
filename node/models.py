from django.db import models

# Create your models here.
class Node(models.Model):
    node_id = models.AutoField(primary_key=True, verbose_name='节点编号')
    node_name = models.CharField(max_length=255, unique=True, verbose_name='主机名')
    node_ip = models.GenericIPAddressField(unique=True, verbose_name='主机IP')
    internal_ip = models.GenericIPAddressField(unique=True, verbose_name='内部IP',  null=True)
    # gputype = models.CharField(max_length=255, verbose_name='GPU类型', null=True)
    gputype = models.JSONField(max_length=255, verbose_name='GPU类型', null=True)
    gpu_num = models.IntegerField(verbose_name='GPU总数', null=True)
    gpu_remain_num = models.IntegerField(verbose_name='GPU剩余数', null=True)

    def __str__(self):
        return self.node_name + ' ' + self.node_ip