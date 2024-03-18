from django.contrib import admin
from .models import Image, Node

# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['image_id', 'name', 'tag', 'source', 'note', 'record_datetime', 'is_push']

# Register your models here.
class NodeAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['node_id', 'node_name', 'node_ip', 'gputype', 'gpu_remain_num', 'gpu_num']

admin.site.register(Image, ImageAdmin)
admin.site.register(Node, NodeAdmin)