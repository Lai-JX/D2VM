from django.contrib import admin
from .models import Image

# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['image_id', 'registry', 'name', 'tag', 'source', 'type', 'commit_date']
admin.site.register(Image, ImageAdmin)