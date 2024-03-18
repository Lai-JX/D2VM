from django.contrib import admin
from .models import Container

# Register your models here.
class ContainerAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['container_id', 'user', 'image', 'pod_name', 'node', 'port', 'gputype', 'num_gpu', 'duration', 'status', 'create_time']




admin.site.register(Container, ContainerAdmin)
