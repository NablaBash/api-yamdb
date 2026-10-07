import re

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from reviews.models import Category, Comment, Genre, Review, Title, User


class SignupSerializer(serializers.Serializer):
    """Регистрация: email + username."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        if not re.fullmatch(r'[\w.@+-]+', value):
            raise serializers.ValidationError(
                'Username может содержать только буквы, цифры и @/./+/-/_.'
            )
        return value

    def validate(self, data):
        username = data['username']
        email = data['email']

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError(
                {'username': 'Этот username уже занят.'}
            )
        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError(
                {'email': 'Этот email уже занят.'}
            )

        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if user is None:
            raise NotFound('Пользователь не найден.')
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class MeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        model = Category

class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        model = Genre


class WriteTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Год выпуска произведения не может быть больше текущего'
            )
        return value


class ReadTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating',
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        view = self.context.get('view')
        if view.action != 'create':
            return data

        user = self.context['request'].user
        title_id = view.kwargs.get('title_id')
        if user.reviews.filter(title=title_id).exists():
            raise ValidationError('Нельзя оставлять отзыв повторно.')

        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)
