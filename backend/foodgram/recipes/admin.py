from django.contrib import admin
# from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
# from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from .models import (Tag, RecipeTag, Ingredient, 
    RecipeIngredient, Recipe, Follow, Favorite,
)

# class OutstandingTokenAdmin(OutstandingTokenAdmin):
#     def has_delete_permission(self, *args, **kwargs):
#         return True # or whatever logic you want
    
#     def get_actions(self, request):
#         actions = super(OutstandingTokenAdmin, self).get_actions(request)
#         if 'delete_selected' in actions:
#             del actions['delete_selected']
#         return actions

# admin.site.unregister(OutstandingToken)
# admin.site.register(OutstandingToken, OutstandingTokenAdmin)

@admin.register(Tag)
class TagClass(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )

@admin.register(Ingredient)
class IngredientClass(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )

admin.site.register(Recipe)
admin.site.register(Follow)
admin.site.register(Favorite)