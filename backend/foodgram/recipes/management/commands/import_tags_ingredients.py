import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from recipes.models import Tag, Ingredient

Models = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv'
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
                    self.stdout.write(f'Данные таблицы {model.__name__} успешно загружены')
                except IntegrityError:
                    return f'Такие экземляры {model} уже существуют...'
        return 'Данные тегов и ингредиентов загружены.'