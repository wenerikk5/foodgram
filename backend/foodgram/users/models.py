from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import RegexUsernameValidator, validate_username_not_me


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[RegexUsernameValidator, validate_username_not_me]
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False
    )
    email = models.EmailField(
        'Почта',
        max_length=254,
        unique=True
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_admin(self):
        return self.is_staff
    
    def __str__(self):
        return f'{self.username}'
