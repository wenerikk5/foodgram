from django.contrib import admin
from django.db.models import Count

from recipes.models import (Tag, Ingredient, 
    RecipeIngredient, Recipe, Subscribe, 
    # Favorite,
)


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    # autocomplete_fields = ('ingredient',)
    # search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientAdmin,)
    list_display = (
        'id', 'name', 'author', 'text', 'pub_date', 'favorite_count'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags', 'pub_date')
    filter_vertical = ('tags',)
    empty_value_display = '-пусто-'

    def favorite_count(self, obj):
        return obj.obj_count
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            obj_count=Count("favorite_recipe", distinct=True),
        )

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Subscribe)
# admin.site.register(Favorite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)