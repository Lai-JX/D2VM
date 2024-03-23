from django.contrib import admin
from .models import User
# from django.contrib.auth.admin import UserAdmin

# Register your models here.
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    search_fields = ('user_id',)
    list_per_page = 10
    list_display = ['user_id', 'username', 'email', 'is_active',]
admin.site.register(User, UserAdmin)