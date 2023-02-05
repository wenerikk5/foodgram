from rest_framework.mixins import (ListModelMixin, RetrieveModelMixin,
    CreateModelMixin, DestroyModelMixin)
from rest_framework.viewsets import GenericViewSet

class ListRetrieveModelMixin(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    pass

class CreateDestroyMixin(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    pass
