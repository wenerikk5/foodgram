### Foodgram - Продуктовый помощник
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

---

Приложение для кулинарных рецептов. Пользователи могут публиковать рецепты, формировать список избранных рецпетов, подписываться на публикации других пользователей.
Сервис "Список покупок" позволяет создать консолидированный список продуктов из выбранных рецептов. Список будет загружен в виде текстового файла в формате .txt.

В рамках проекта был разработан весь backend на REST API. Проект запускается с помощью docker compose.

## Установка и настройка приложения

```bash
git clone <project>
cd foodgram/infra/
# Переименуйте .env-example в .env (или создайте свой)
mv .env-example .env
```

## Docker
```bash
# Сборка и запуск в фоновом режиме. Миграции и сборка статики уже будут выполнены.
docker compose up -d
# Заполнение базы тегами и ингредиентами
docker compose exec backend python manage.py import_tags_ingredients
# Добавление пользователей (для тестового режима с упрощенными паролями)
docker compose exec backend python manage.py import_users
# Добавление тестовых рецептов (после добавление тегов, ингредиентов и пользователей)
docker compose exec backend python manage.py import_recipes
```

## Доступ тестового пользователя и администратора
Вход на сайт потребует ввода почты и пароля пользователя.

Аутентификация тестового пользователя (если добавлены командой import_users):
```bash
http://localhost/
email: john@gmail.com
password: 123
```
Вход в админ зону потребует логина и пароля.
```bash
http://localhost/admin
login: root
password: 123
```

## Документация

Документация API доступна по адресу: http://localhost/redoc

##Эндпоинты к API (Postman)

**Регистрация нового пользователя:**
POST http://localhost/api/users/
```json
{
    "email": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "password": "..."
}
```
**Получение токена:**
POST http://localhost/api/auth/token/login/
```json
{
    "email": "...",
    "password": "..."
}
```

## Использованные технологии**

Python 3.10, Django 3.2, DRF, Nginx, Gunicorn, Docker, PostgreSQL, Git

## Превью

<img src="https://github.com/wenerikk5/foodgram/backend/foodgram/media/recipes/images/preview.png" alt="img" width="600" height='400'>