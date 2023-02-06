import csv
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка данных из csv файлов'

    def handle(self, *args, **options):
        with open(
            f'{settings.BASE_DIR}/data/users.csv',
            'r',
            encoding='utf-8'
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    u = User(
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        is_superuser=bool(row['is_superuser']),
                        is_staff=bool(row['is_staff'])
                    )
                    u.set_password(row['password'])
                    u.save()
                except IntegrityError:
                    return 'Такие Пользователи уже есть...'
        return (f'Пользователи успешно созданы')
