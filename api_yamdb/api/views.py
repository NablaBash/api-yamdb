from rest_framework import viewsets, mixins, filters
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    ReadTitleSerializer,
    WriteTitleSerializer
)
from .permissions import IsAdminOrReadOnly
from reviews.models import Category, Genre, Title
from .filters import TitleFilter


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'title_id'
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadTitleSerializer
        return WriteTitleSerializer
