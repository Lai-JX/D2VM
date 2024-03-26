from django.contrib import admin
from .models import Node


# Register your models here.
class NodeAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['node_id', 'node_name', 'node_ip', 'internal_ip', 'gputype', 'gpu_remain_num', 'gpu_num']

admin.site.register(Node, NodeAdmin)