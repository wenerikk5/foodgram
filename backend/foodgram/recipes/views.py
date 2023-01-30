from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from rest_framework import filters, status, viewsets, serializers
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from recipes.models import *
from users.models import User
from .serializers import (UserSerializer, AccountSerializer, 
    TokenSerializer, PasswordUpdateSerializer, TagSerializer,
    RecipeTagSerializer, IngredientSerializer, RecipeIngredientSerializer,
    RecipeSerializer, FollowingSerializer, FavoritesSerializer,
)
from .mixins import ListRetrieveModelMixin
# from .utils import get_tokens_for_user


class UserViewSet(viewsets.ModelViewSet):
    """Registration of a new User. List all users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

    @action(
        methods=['GET',],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=AccountSerializer
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def user_auth(request):
#     """Getting login token."""
#     serializer = TokenSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
   
#     user = get_object_or_404(
#         User,
#         email=serializer.validated_data.get('email')
#     )
    
#     if not check_password(serializer.validated_data.get('password'), user.password):
#         return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

#     response = get_tokens_for_user(user)
#     user.refresh_token = response['refresh']
#     user.save()
#     return Response(
#         {
#             "auth_token": response['access'],
#             "refresh": response['refresh']
#         },
#         status=status.HTTP_200_OK
#     )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_password_change(request):
    """Changing of User's password."""

    serializer = PasswordUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not check_password(
        serializer.validated_data.get('current_password'),
        request.user.password
    ):
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(username=request.user.username)
    user.set_password(serializer.validated_data.get('new_password'))
    user.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """Disactivating current token on Logout."""

    user = User.objects.get(username=request.user.username)
    token = RefreshToken(user.refresh_token)
    token.blacklist()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):

        self.validate_nested_data(request.data)

        # Remove 'tags' and 'ingredients' from data.
        data = {
            'tags': request.data.pop('tags'),
            'ingredients': request.data.pop('ingredients')
        }

        # Use fake tag and ingredient to pass validation of nested items.
        request.data['tags'] = [{
            "name": "Завтрак",
            "color": "#E26C2DFF",
            "slug": "slug"
        },]

        request.data['ingredients'] = [{
            "name": "1",
            "amount": "10"
        },]

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, data):
        # Adding original 'tags' and 'ingredients' in request.
        serializer.save(
            author=self.request.user,
            tags=data['tags'],
            ingredients=data['ingredients'])

    def validate_nested_data(self, data):
        # 'tags' list exist and not empty.
        try:
            tags = data.get('tags')
        except:
            raise serializers.ValidationError(
                    {
                        'tags':f"Tags must be selected!"
                    }
                )
        if len(tags) == 0:
            raise serializers.ValidationError(
                    {
                        'tags':f"Tags must be selected!"
                    }
                )
        # 'ingredients' list exist and not empty.
        try:
            ingredients = data.get('ingredients')
        except:
            raise serializers.ValidationError(
                    {
                        'ingredients':f"Ingredients must be added!"
                    }
                )
        if len(ingredients) < 1:
            raise serializers.ValidationError(
                    {
                        'ingredients':f"Ingredients must be added!"
                    }
                )

        # 'tags' and 'ingredients' items are exist instances of models.
        for tag in tags:
            try:
                current_tag = Tag.objects.get(id=tag)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {
                        'tags':f"Tag with id={tag} doesn't exist!"
                    }
                )
        for ingredient in ingredients:
            try:
                current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {
                        'ingredients:': f'Ingredient with id={ingredient["id"]} do not exist!'
                    }
                )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        self.validate_nested_data(request.data)

        # Remove 'tags' and 'ingredients' from data.
        data = {
            'tags': request.data.pop('tags'),
            'ingredients': request.data.pop('ingredients')
        }

        # Use fake tag and ingredient to pass validation of nested items.
        request.data['tags'] = [{
            "name": "Завтрак",
            "color": "#E26C2DFF",
            "slug": "slug"
        },]

        request.data['ingredients'] = [{
            "name": "1",
            "amount": "10"
        },]

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, data)
            
        
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
    
    def perform_update(self, serializer, data):
        serializer.save(tags=data['tags'], ingredients=data['ingredients'])

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class SubscribeView(APIView):
    """Create/delete subscribtion."""
    permission_classes=[IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        subs = request.user.follower.all()
        sub_ids = []
        for sub in subs:
            sub_ids.append(sub.author.id)

        all = User.objects.all().filter(id__in=sub_ids)

        serializer = FollowingSerializer(self.paginate_queryset(all), many=True)

        return self.get_paginated_response(
            serializer.data)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data) 

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        created = False

        if request.user != author:
            _, created = Follow.objects.get_or_create(
                user=request.user,
                author=author
            )

        serializer = FollowingSerializer(author, context={'request': request})

        if created:
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)

        try:
            Follow.objects.get(
                user=request.user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FavoriteView(APIView):
    """Create/delete recipe in favorites."""
    permission_classes=[IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        created = False

        if request.user != recipe.author:
            _, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )

        serializer = FavoritesSerializer(recipe)

        if created:
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        try:
            Favorite.objects.get(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartView(APIView):
    """Add/delete recipe in shopping cart."""
    permission_classes=[IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        created = False

        if request.user != recipe.author:
            _, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )

        serializer = FavoritesSerializer(recipe)

        if created:
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        try:
            ShoppingCart.objects.get(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)