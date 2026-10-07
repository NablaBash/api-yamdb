from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter

from .permissions import IsAdminOrReadOnly


class ReferenceViewSetMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
