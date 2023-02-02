from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from djoser.serializers import (PasswordSerializer,
    UserCreateSerializer, UserSerializer
)

from recipes.models import (Tag, RecipeTag, Ingredient, IngredientList,
    RecipeIngredient, Recipe, Subscribe, ShoppingCart,
)
from drf_extra_fields.fields import Base64ImageField

User = get_user_model()


class AccountListSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            )
    
    def get_is_subscribed(self, obj):
        try:
            obj.follower.all().get(author=self.context.get("request").user)
            return True
        except:
            return False


class AccountCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            )
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    # def create(self, validated_data):
    #     user = User(
    #         email=validated_data['email'],
    #         username=validated_data['username'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name']
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user


class TokenSerializer(serializers.Serializer):
    """Creation of tokens for login."""

    email = serializers.EmailField(
        max_length=254
    )
    password = serializers.CharField(max_length=150)


class PasswordChangeSerializer(PasswordSerializer):
    current_password = serializers.CharField(
        max_length=150,
        required=True,
    )

    def validate(self, data):
        user = self.context.get('request').user
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                    "new_password": "Пароли не должны совпадать!"
            })
        if not check_password(data.get('current_password'), user.password):
            raise serializers.ValidationError({
                    "current_password": "Неверный пароль!"
            })     
        return data

class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug')
        read_only_fields = ('name', 'color', 'slug')
        # extra_kwargs = {
        #     'name': {'validators': []},
        #     'color': {'validators': []},
        #     'slug': {'validators': []},
        # }


class RecipeTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit')


class IngredientListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    measurement_unit = serializers.SerializerMethodField(read_only=True)
    name = serializers.ReadOnlyField(source='name.name')
    
    class Meta:
        model = IngredientList
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit'
        )

    def get_measurement_unit(self, obj):
        unit = Ingredient.objects.get(id=obj.id).measurement_unit
        return unit


class RecipeIngredientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = IngredientList
        fields = (
            'id',
            'name',
            'amount',
            # 'measurement_unit'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = AccountListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientListSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',            
            'name',
            'image',
            'text',
            'cooking_time',
        )
    
    def get_is_favorited(self, obj):
        try:
            obj.favorites.all().get(user=self.context.get("request").user)
            return True
        except:
            return False

    
    def get_is_in_shopping_cart(self, obj):
        try:
            obj.shopping_cart.all().get(user=self.context.get("request").user)
            return True
        except:
            return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = AccountListSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientListSerializer(many=True)
    image=Base64ImageField(use_url=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',          
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, attrs):
        try:
            tags = attrs.get('tags')
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
            ingredients = attrs.get('ingredients')
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

        # 'ingredients' items are exist instances of models.
        for ingredient in ingredients:
            try:
                current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {
                        'ingredients:': f'Ingredient with id={ingredient["id"]} do not exist!'
                    }
                )
        return attrs

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            instance = IngredientList.objects.create(
                name=current_ingredient,
                amount=ingredient['amount']
            )
            RecipeIngredient.objects.create(
                ingredient_list=instance,
                recipe=recipe,
            )

    def create(self, validated_data):
        print("====Validated data:", validated_data)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        tag_ids = [tag['id'] for tag in tags]
        print('=====tag_ids:', tag_ids)
        recipe.tags.set(tag_ids)
        # for tag in tags:
        #     current_tag = Tag.objects.get(id=tag['id'])
        #     RecipeTag.objects.create(
        #         tag=current_tag,
        #         recipe=recipe
        #     )
        self.create_ingredients(ingredients, recipe)
        
        return recipe

    def update(self, instance, validated_data):
        print("=====UPDATE in serializer")
        if 'tags' in validated_data:
            tag_ids = [tag['id'] for tag in validated_data.pop('tags')]
            instance.tags.set(tag_ids)
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        
        return super().update(
            instance, validated_data
        )
    
    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data

class RecipeSubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

class SubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            )
    
    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = RecipeSubscribeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return len(obj.recipes.all())
    
    def get_is_subscribed(self, obj):
        try:
            obj.follower.all().get(author=self.context.get("request").user)
            return True
        except:
            return False

class FavoritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
