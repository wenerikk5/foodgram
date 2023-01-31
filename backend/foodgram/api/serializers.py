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
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug')


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


class RecipeSerializer(serializers.ModelSerializer):
    author = AccountListSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientListSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image=Base64ImageField(use_url=True, required=False)

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

    
    def create(self, validated_data):
        print("====Validated data:", validated_data)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        
        for tag in tags:
            current_tag = Tag.objects.get(id=tag)
            RecipeTag.objects.create(
                tag=current_tag,
                recipe=recipe
            )
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
        return recipe

    def update(self, instance, validated_data):

        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')

        # Create list of actual tags.
        tag_ids_to_save = []

        for tag in tags:
            current_tag = Tag.objects.get(id=tag)
            # Check if instance exists. If so, delete from delete_list.
            obj, created = RecipeTag.objects.get_or_create(
                tag=current_tag,
                recipe=instance
            )
            tag_ids_to_save.append(obj.id)

        print("===tag_ids_to_save:", tag_ids_to_save)
        # Create list to delete considering ids to save.
        tags_to_delete=RecipeTag.objects \
            .filter(recipe__id=instance.id) \
            .exclude(id__in=tag_ids_to_save)
        print("===tag_ids_to_delete:", tags_to_delete)
        if len(tags_to_delete) > 0:
            for item in tags_to_delete:
                item.delete()
        
        # Remove all current IngredientList instances.
        # Corresponding RecipeIngredient instances be auto delete by CASCADE.
        related_recipe_ingredients = RecipeIngredient.objects \
            .filter(recipe__id=instance.id)

        ingredient_list_ids_to_remove = []

        for item in related_recipe_ingredients:
            ingredient_list_ids_to_remove.append(item.ingredient_list.id)

        ingredient_list_to_remove = IngredientList.objects \
            .filter(id__in=ingredient_list_ids_to_remove)

        if len(ingredient_list_to_remove) > 0:
            for ingredient_item in ingredient_list_to_remove:
                ingredient_item.delete()

        # Create new ingredients like in Create method.
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            object = IngredientList.objects.create(
                name=current_ingredient,
                amount=ingredient['amount']
            )
            RecipeIngredient.objects.create(
                ingredient_list=object,
                recipe=instance,
            )      
        
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', 
            instance.cooking_time)
        instance.save()

        return instance

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
