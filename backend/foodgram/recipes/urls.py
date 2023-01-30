from django.urls import include, path
from rest_framework.routers import DefaultRouter
from recipes.views import (UserViewSet,
    user_password_change, user_logout, TagViewSet,
    IngredientViewSet, RecipeViewSet, SubscribeView,
    FavoriteView, ShoppingCartView,
)
from rest_framework.authtoken import views
from .utils import MyTokenObtainPairView

app_name = 'recipes'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('users/set_password/', user_password_change),
    path('users/subscriptions/', SubscribeView.as_view()),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view()),
    path('recipes/<int:pk>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartView.as_view()),
    path('', include(router.urls)),
    # path('auth/token/login/', MyTokenObtainPairView.as_view(), name='get_token'),
    # path('auth/token/logout/', user_logout),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/', views.obtain_auth_token),

    ]
