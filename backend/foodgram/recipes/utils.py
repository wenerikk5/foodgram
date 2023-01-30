from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, get_list_or_404, get_object_or_404
from users.models import User


# if api_settings.BLACKLIST_AFTER_ROTATION:
#     from .token_blacklist.models import BlacklistedToken


# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     print("=====Refreshtoken: ", refresh)
#     print("refresh.access_token: ", refresh.access_token)
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token)
#     }


# def get_token_for_user(user):
#     """Получение токена авторизации."""

#     access = AccessToken.for_user(user)
#     refresh = RefreshToken.for_user(user)
#     return {'token': str(access)}

class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super().__init__(*args, **kwargs)


class TokenObtainSerializer(serializers.Serializer):
    email_field = get_user_model().EMAIL_FIELD

    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials'),
        'no_confirmation': _("Wrong password!")
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.email_field] = serializers.EmailField()
        self.fields['password'] = PasswordField()

    def validate(self, attrs):
        authenticate_kwargs = {
            self.email_field: attrs[self.email_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        # self.user = authenticate(**authenticate_kwargs)

        try:
            self.user = User.objects.get(email=authenticate_kwargs['email'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )

        if not check_password(authenticate_kwargs['password'], self.user.password):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_confirmation"],
                "no_active_account",
            )

        # if not api_settings.USER_AUTHENTICATION_RULE(self.user):
        #     raise exceptions.AuthenticationFailed(
        #         self.error_messages['no_active_account'],
        #         'no_active_account',
        #     )

        return {}

    @classmethod
    def get_token(cls, user):
        raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializer` subclasses')


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        print("=====attrs:", attrs)

        user = get_object_or_404(
            User,
            email=attrs.get('email')
        )
        
        user.refresh_token = data['refresh']
        user.save()

        # if api_settings.UPDATE_LAST_LOGIN:
        #     update_last_login(None, self.user)

        return {'auth_token': data['access']}
#####
#####
#####
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Add custom claims
#         token['name'] = user.name
#         # ...

#         return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    permission_classes = (AllowAny,)