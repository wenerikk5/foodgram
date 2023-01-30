from django.contrib import admin
from .models import User

@admin.register(User)
class UserClass(admin.ModelAdmin):

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'password',
        'email',
        'role',
        'is_staff',
        'is_active',
    )
    list_filter = (
        'role',
        'last_login',
    )
    search_fields = (
        'username',
        'email',
        'role',
    )
