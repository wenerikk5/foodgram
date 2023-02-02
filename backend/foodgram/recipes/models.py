from django.db import models
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Наименование тега',
        max_length=150,
        unique=True,
    )
    color = ColorField(
        'Цвет',
        format="hexa",
        unique=True,
    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=150,
        unique=True,
        db_index=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.slug}'


class Ingredient(models.Model):
    name = models.CharField(
        'Наименование ингредиента',
        max_length=150
    )
    measurement_unit = models.CharField(
        'Ед. изм.',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_connection'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class IngredientList(models.Model):
    name = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE, 
        related_name='ingredient_list'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1),]
    )

    def __str__(self):
        return (f'{self.name}-{self.amount}')


class RecipeIngredient(models.Model):
    ingredient_list = models.ForeignKey(
        IngredientList,
        on_delete=models.CASCADE, 
        related_name='ri'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE, 
        related_name='ri'
    )

    def __str__(self):
        return (f'{self.ingredient_list}')


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=100,
        unique=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images',
        blank=True
    )
    text = models.TextField(
        'Текст рецепта'
    )
    cooking_time = models.PositiveIntegerField()
    tags = models.ManyToManyField(
        Tag,
        through=RecipeTag,
        blank=False,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        IngredientList,
        through=RecipeIngredient,
        blank=False,
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']


    FIELDS_INFO = (
        'Author: {author};'
        'Name: {name};'
        'Text: {text};'
        'Cooking time: {cooking_time};'
        'Tags: {tags};'
        'Ingredients: {ingredients}'
    )

    def __str__(self):
        return self.FIELDS_INFO.format(
            author=self.author,
            name=self.name,
            text=self.text,
            cooking_time=self.cooking_time,
            tags=self.tags,
            ingredients=self.ingredients
        )


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True
    )

    def __str__(self):
        return self.author.username


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorite_user',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shopping_cart_user',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.recipe.name}'