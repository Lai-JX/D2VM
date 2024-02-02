from django.contrib import admin
from .models import Container, Node

# Register your models here.
class ContainerAdmin(admin.ModelAdmin):
    list_per_page = 10
    # list_display = ['container_id', 'user', 'image', 'pod_name', 'node', 'port', 'gputype', 'num_gpu', 'duration', 'published_date']

class NodeAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['node_id', 'node_name', 'node_ip', 'gputype']


admin.site.register(Container, ContainerAdmin)
admin.site.register(Node, NodeAdmin)