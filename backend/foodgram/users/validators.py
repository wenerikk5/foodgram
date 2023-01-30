from datetime import datetime

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


class RegexUsernameValidator(UnicodeUsernameValidator):
    """Validation of allowed symbols in username."""

    regex = r'^[\w.@+-]+\z'


def validate_username_not_me(value):
    """Do not allow to have username=me."""

    if value == 'me':
        raise ValidationError('Username "me" is not allowed!')
    return value
