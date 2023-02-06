from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from djoser.serializers import (PasswordSerializer,
    UserCreateSerializer, UserSerializer
)

from recipes.models import (Tag, Ingredient, 
    RecipeIngredient, Recipe, Subscribe, 
    FavoriteRecipe, ShoppingCart
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
        return (
            self.context.get('request').user.is_authenticated
            and
            Subscribe.objects.filter(
                user=self.context.get("request").user,
                author=obj
            ).exists()
        )


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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    
    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit'
        )


class IngredientCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    
    class Meta:
        model = Ingredient
        fields = (
            'id',
            # 'name',
            'amount',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = AccountListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientListSerializer(many=True, source='recipe')
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
        user=self.context.get("request").user
        return (
            user.is_authenticated
            and
            FavoriteRecipe.objects.filter(
                user=user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user=self.context.get("request").user
        return (
            user.is_authenticated
            and
            ShoppingCart.objects.filter(
                user=user,
                recipe=obj
            ).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    # tags = TagSerializer(many=True)
    ingredients = IngredientCreateUpdateSerializer(many=True)
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
        print("=====Attrs for validation:", attrs)
        # Name is not shorted than 3 letters.
        if len(attrs.get('name')) < 3:
            raise serializers.ValidationError({
                'name': 'Минимальная длина названия 3 символа'
            })

        # Duplication of tags.
        tags = attrs.get('tags')
        print('===Tags:', tags)
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': 'Тэги не должны дублироваться'
            })

        # 'ingredients' list exist, consist of several elements, \
        # elements exist and unique.
        try:
            ingredients = attrs['ingredients']
        except:
            raise serializers.ValidationError({
                    'ingredients:': 'Обязательное поле для заполнения'
                })
        if len(set([item['id'] for item in ingredients])) < 2:
            raise serializers.ValidationError({
                    'ingredients:': 'Ингредиентов должно быть не менее двух.'
                })

        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError({
                    'ingredients:': f'Ингредиент с id={ingredient["id"]} \
                        не существует в базе'
                })
        if len(ingredients) != len(set([item['id'] for item in ingredients])):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны дублироваться'
            })
        
        # Amount is not lower than 1 unit.
        amounts = attrs.get('ingredients')
        if [item for item in amounts if item['amount'] < 1]:
            raise serializers.ValidationError({
                'amount': 'Количество ингредиента не должно быть менее 1'
            })

        # Cooking_time is not less that 1 minute.
        cooking_time = attrs.get('cooking_time')
        if cooking_time < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Продолжительность не должна быть менее 1 мин.'
            })        
        return attrs

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient.get('id'))
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            # RecipeIngredient.objects.bulk_create([
            #     RecipeIngredient(
            #         recipe=recipe,
            #         ingredient_id=ingredient.get('id'),
            #         amount=ingredient.get('amount'),
            #     )
            # ])


    def create(self, validated_data):
        tags = validated_data.pop('tags')
        print("=====Validated data Tag:", tags)
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        # for tag in tags:
        #     current_tag = Tag.objects.get(id=tag['id'])
        #     RecipeTag.objects.create(
        #         tag=current_tag,
        #         recipe=recipe
        #     )
        self.create_ingredients(ingredients, recipe)
        
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
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
    email = serializers.CharField(
        source='author.email',
        read_only=True)
    id = serializers.IntegerField(
        source='author.id',
        read_only=True)
    username = serializers.CharField(
        source='author.username',
        read_only=True)
    first_name = serializers.CharField(
        source='author.first_name',
        read_only=True)
    last_name = serializers.CharField(
        source='author.last_name',
        read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField(
        source='author.recipe.count')

    class Meta:
        model = Subscribe
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

    def validate(self, attrs):
        user = self.context.get('request').user
        author = self.context.get('author_id')
        
        if user.id == int(author):
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя'
            })
        if Subscribe.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на этого автора'
            })
        return attrs

    def get_recipes(self, obj):
        recipes = obj.author.recipe.all()
        return RecipeSubscribeSerializer(
            recipes,
            many=True
        ).data

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            user=self.context.get('request').user,
            author=obj.author
        ).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='recipe.id',
        read_only=True)
    name = serializers.CharField(
        source='recipe.name',
        read_only=True)
    image = serializers.CharField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = FavoriteRecipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def validate(self, attrs):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        
        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в списке избранного'
            })
        return attrs


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='recipe.id',
        read_only=True)
    name = serializers.CharField(
        source='recipe.name',
        read_only=True)
    image = serializers.CharField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def validate(self, attrs):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в списке покупок'
            })
        return attrs