from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (CustomUserViewSet, TagViewSet,
    IngredientViewSet, RecipeViewSet, SubscribeViewSet,
    FavoriteRecipeViewSet, ShoppingCartRecipeViewSet
)
from rest_framework.authtoken import views

app_name = 'api'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(
    r'users/(?P<user_id>\d+)/subscribe', SubscribeViewSet,
    basename='subscribe')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteRecipeViewSet,
    basename='favorite')
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartRecipeViewSet,
    basename='shopping_cart')



urlpatterns = [
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    ]
