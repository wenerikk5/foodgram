from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
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
    # FavoritesSerializer,
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

class SubscribeView(CreateDestroyMixin):
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


# class FavoriteView(APIView):
#     """Create/delete recipe in favorites."""
#     permission_classes=[IsAuthenticated]

#     def post(self, request, recipe_id):
#         recipe = get_object_or_404(Recipe, pk=recipe_id)
#         created = False

#         if request.user != recipe.author:
#             _, created = Favorite.objects.get_or_create(
#                 user=request.user,
#                 recipe=recipe
#             )

#         serializer = FavoritesSerializer(recipe)

#         if created:
#             return Response(
#                 serializer.data,
#                 status=status.HTTP_201_CREATED
#             )

#         return Response(status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, recipe_id):
#         recipe = get_object_or_404(Recipe, pk=recipe_id)

#         try:
#             Favorite.objects.get(
#                 user=request.user,
#                 recipe=recipe
#             ).delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# class ShoppingCartView(APIView):
#     """Add/delete recipe in shopping cart."""
#     permission_classes=[IsAuthenticated]

#     def post(self, request, recipe_id):
#         recipe = get_object_or_404(Recipe, pk=recipe_id)
#         created = False

#         if request.user != recipe.author:
#             _, created = ShoppingCart.objects.get_or_create(
#                 user=request.user,
#                 recipe=recipe
#             )

#         serializer = FavoritesSerializer(recipe)

#         if created:
#             return Response(
#                 serializer.data,
#                 status=status.HTTP_201_CREATED
#             )

#         return Response(status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, recipe_id):
#         recipe = get_object_or_404(Recipe, pk=recipe_id)

#         try:
#             ShoppingCart.objects.get(
#                 user=request.user,
#                 recipe=recipe
#             ).delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except:
#             return Response(status=status.HTTP_400_BAD_REQUEST)