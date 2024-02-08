from django.contrib import admin
from .models import Image

# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['image_id', 'name', 'tag', 'source', 'note', 'record_datetime']
admin.site.register(Image, ImageAdmin)