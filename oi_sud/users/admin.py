# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

class CustomUserAdmin(UserAdmin):

    model = CustomUser
    list_display = ['email', 'username',]

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('regions',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)