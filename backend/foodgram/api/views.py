from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from rest_framework import filters, status, viewsets, serializers
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly, SAFE_METHODS)
from djoser.views import UserViewSet
from recipes.models import *
from .filters import IngredientFilter, RecipeFilter

from .serializers import (AccountCreateSerializer, AccountListSerializer, 
    PasswordChangeSerializer, TagSerializer, IngredientSerializer,
    IngredientListSerializer, IngredientCreateUpdateSerializer,
    RecipeReadSerializer, RecipeWriteSerializer, SubscribeSerializer, 
    FavoriteSerializer, ShoppingCartRecipeSerializer,
)
from .mixins import ListRetrieveModelMixin, CreateDestroyMixin
from .permissions import IsAuthorOrReadOnly

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Create User, set new password, get 'me' page, get subscribers list."""
    
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'set_password':
            return PasswordChangeSerializer
        if self.action == 'create':
            return AccountCreateSerializer
        return AccountListSerializer

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = Subscribe.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ListRetrieveModelMixin):
    """Получение списка тегов и просмотр отдельного тега по его id."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ListRetrieveModelMixin):
    """
    Получение списка ингредиентов и просмотр отдельного ингредиента
    по его id.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(
        methods=('get',),
        detail=False,
        url_path='download_shopping_cart',
        pagination_class=None
    )
    def download_shopping_cart(self, request):
        if not request.user.shopping_cart_user.exists():
            return Response(
                'В корзине нет товаров',
                status=status.HTTP_400_BAD_REQUEST
            )
        
        text = 'Список покупок:\n'
        ingredient_name = 'recipe__recipe__ingredient__name'
        ingredient_unit = 'recipe__recipe__ingredient__measurement_unit'
        recipe_amount = 'recipe__recipe__amount'
        amount_sum = 'recipe__recipe__amount__sum'
        cart = request.user.shopping_cart_user.select_related('recipe').values(
            ingredient_name, ingredient_unit).annotate(
                Sum(recipe_amount)).order_by(ingredient_name)
        i = 1
        for _ in cart:
            text += (
                f'{i}. {_[ingredient_name].capitalize()}'
                f' - {_[amount_sum]}, {_[ingredient_unit]}\n'
            )
            i += 1
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class SubscribeViewSet(CreateDestroyMixin):
    """Create/delete subscribtion."""
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.follower.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author_id'] = self.kwargs.get('user_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            author=get_object_or_404(
                User,
                id=self.kwargs.get('user_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        try:
            Subscribe.objects.get(
                user=request.user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(
                {'errors': 'Вы не были подписаны на автора'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FavoriteRecipeViewSet(CreateDestroyMixin):
    """Create/delete favorite receipt."""
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        # user = self.request.user
        return self.request.user.favorite_user.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        try:
            get_object_or_404(
                FavoriteRecipe,
                user=request.user,
                recipe_id=recipe_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(
                {'errors': 'Рецепт отсутствует в Вашем списке избранного'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ShoppingCartRecipeViewSet(CreateDestroyMixin):
    """Add/delete recipt in shopping list ."""
    serializer_class = ShoppingCartRecipeSerializer

    def get_queryset(self):
        return self.request.user.shopping_cart_user.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        try:
            get_object_or_404(
                ShoppingCart,
                user=request.user,
                recipe_id=recipe_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(
                {'errors': 'Рецепт отсутствует в Вашем списке избранного'},
                status=status.HTTP_400_BAD_REQUEST
            )
