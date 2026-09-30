from django_filters import rest_framework as filter

from reviews.models import Title


class TitleFilter(filter.FilterSet):
    category = filter.CharFilter(field_name='category__slug')
    genre = filter.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('name', 'year')
