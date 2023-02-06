import csv
import os
from datetime import datetime
from django.contrib.auth import get_user_model
from recipes.models import (Ingredient, Tag, RecipeIngredient,
    Recipe, Subscribe,
)

User = get_user_model()


def run():
    """Заполняем данные моделей информацией из CSV таблиц."""

    with open('./data/tags.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            t = Tag(
                name=row['name'],
                color=row['color'],
                slug=row['slug']
            )
            t.save()
        print("=====TAGS ADDED=====")
    
    with open('./data/users.csv') as file:
        admin = User(
            username='root',
            email='root@root.com',
            is_superuser=True
        )
        admin.set_password('123')
        admin.save()

        reader = csv.DictReader(file)
        for row in reader:
            u = User(
                username=row['username'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
            )
            u.set_password(row['password'])
            u.save()
        print("=====USERS ADDED=====")

    with open('./data/ingredients.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            p = Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            p.save()
        print("=====INGREDIENTS ADDED=====")
    

    with open('./data/recipes.csv') as file:
        reader = csv.DictReader(file)
        tag = Tag.objects.first()
        tags = [tag,]
        for row in reader:
            date = datetime.now()
            author = User.objects.get(id=row['author_id'])
            p = Recipe(
                name=row['name'],
                text=row['text'],
                cooking_time=row['cooking_time'],
                author=author,
                pub_date=date
            )
            p.save()
            p.tags.set(tags)
        print('=====Recipes Added=====')


    # with open('./data/recipe_tags.csv') as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         recipe = Recipe.objects.get(id=row['recipe_id'])
    #         tag = Tag.objects.get(id=row['tag_id'])
    #         p = RecipeTag(
    #             recipe=recipe,
    #             tag=tag
    #         )
    #         p.save()
    #     print('=====RecipeTags added=====')


    with open('./data/recipe_ingredients.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            recipe = Recipe.objects.get(id=row['recipe_id'])
            ingredient = Ingredient.objects.get(id=row['ingredient_id'])
            p = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=row['amount']
            )
            p.save()
        print('=====RecipeIngerdients added=====')


    # with open('./data/subscribes.csv') as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         user = User.objects.get(id=row['user_id'])
    #         author = User.objects.get(id=row['author_id'])
    #         date = datetime.now()
    #         p = Subscribe(
    #             user=user,
    #             author=author,
    #             created=date
    #         )
    #         p.save()
    #     print('=====Subscribes added=====')
