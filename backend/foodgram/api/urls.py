from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (CustomUserViewSet, TagViewSet,
    IngredientViewSet, RecipeViewSet, SubscribeView,
    FavoriteView, ShoppingCartView,
)
from rest_framework.authtoken import views

app_name = 'api'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    # path('users/subscriptions/', SubscribeView.as_view()),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view()),
    path('recipes/<int:pk>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartView.as_view()),
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    ]
