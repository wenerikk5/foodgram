import csv
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from recipes.models import Recipe, RecipeIngredient

User = get_user_model()


Models = {
    Recipe: 'recipes.csv',
    Recipe.tags.through: 'recipe_tags.csv',
    RecipeIngredient: 'recipe_ingredients.csv',
}


class Command(BaseCommand):
    help = 'Загрузка данных из csv файлов'

    def handle(self, *args, **options):
        for model, csv_files in Models.items():
            with open(
                f'{settings.BASE_DIR}/data/{csv_files}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                try:
                    model.objects.bulk_create(
                        model(**data) for data in reader
                    )
                except IntegrityError:
                    return f'Такие экземляры {model} уже существуют...'
                self.stdout.write(f'Данные таблицы {model.__name__} успешно загружены')
        return 'Рецепты загружены.'
