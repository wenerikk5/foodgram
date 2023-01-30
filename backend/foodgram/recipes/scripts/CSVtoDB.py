import csv
import os
from recipes.models import Ingredient, Tag


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

    with open('./data/ingredients.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            p = Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            p.save()
        print("=====INGREDIENTS ADDED=====")

