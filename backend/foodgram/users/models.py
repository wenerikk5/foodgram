from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import RegexUsernameValidator, validate_username_not_me


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexUsernameValidator, validate_username_not_me]
    )
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLES,
        default=USER
    )
    email = models.EmailField(
        'Почта',
        max_length=254,
        unique=True
    )
    refresh_token = models.CharField(max_length=254, blank=True, null=True)

    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff
    
    def is_moderator(self):
        return self.role == self.MODERATOR
