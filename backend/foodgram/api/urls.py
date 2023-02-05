from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (CustomUserViewSet, TagViewSet,
    IngredientViewSet, RecipeViewSet, SubscribeView,
    # FavoriteView, ShoppingCartView,
)
from rest_framework.authtoken import views

app_name = 'api'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(
    r'users/(?P<user_id>\d+)/subscribe', SubscribeView,
    basename='subscribe')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')



urlpatterns = [
    # path('recipes/<int:recipe_id>/favorite/', FavoriteView.as_view()),
    # path('recipes/<int:recipe_id>/shopping_cart/', ShoppingCartView.as_view()),
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    ]
