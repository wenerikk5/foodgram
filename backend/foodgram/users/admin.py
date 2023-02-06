from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmim(admin.ModelAdmin):

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_superuser',
    )
    list_filter = (
        'last_login',
    )
    search_fields = (
        'username',
        'email',
    )
    empty_value_display = '-пусто-'
