import random

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import ReferenceViewSetMixin
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAuthorModeratorAdminOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    MeSerializer,
    ReadTitleSerializer,
    ReviewSerializer,
    SignupSerializer,
    TokenSerializer,
    UserSerializer,
    WriteTitleSerializer,
)


class SignupView(APIView):
    """POST /auth/signup/ — регистрация, отправка кода на email."""

    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        user, _ = User.objects.get_or_create(
            username=username,
            email=email,
        )

        confirmation_code = str(random.randint(100000, 999999))
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            subject='YaMDb confirmation code',
            message=f'Your confirmation code: {confirmation_code}',
            from_email='noreply@yamdb.fake',
            recipient_list=[email],
        )

        return Response(
            {'email': email, 'username': username},
            status=status.HTTP_200_OK,
        )


class TokenView(APIView):
    """POST /auth/token/ — получить JWT по username и коду."""

    permission_classes = []

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        code = serializer.validated_data['confirmation_code']

        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.confirmation_code != code:
            return Response(
                {'confirmation_code': ['Неверный код подтверждения.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserListCreateView(generics.ListCreateAPIView):
    """GET/POST /users/ — только админ."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ['username']


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /users/{username}/ — только админ."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    http_method_names = ['get', 'patch', 'delete']


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /users/me/ — свой профиль."""

    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return self.request.user


class CategoryViewSet(ReferenceViewSetMixin):
    """Категории произведений.
    GET/POST /categories/ — список и создание (POST — только
    Администратор).
    DELETE /categories/{slug}/  — удаление (только Администратор).
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ReferenceViewSetMixin):
    """Жанры произведений.
    GET/POST /genres/ — список и создание (POST — только
    Администратор).
    DELETE /genres/{slug}/  — удаление (только Администратор).
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Произведения.
    GET/POST /titles/ — список и создание (POST — только
    Администратор).
    GET/PATCH/DELETE /titles/{title_id}/ — чтение доступно всем,
    изменение, частичное обновление и удаление — только Администратору.
    PUT не поддерживается.
    """

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    lookup_field = 'id'
    lookup_url_kwarg = 'title_id'
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadTitleSerializer
        return WriteTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Отзывы на произведения.
    GET/POST /titles/{title_id}/reviews/ — список и создание (POST — только
    авторизованным).
    GET/PATCH/DELETE /titles/{title_id}/reviews/{id}/ — чтение доступно всем,
    изменение и удаление — автору, модератору или админу.
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии к отзывам.
    GET/POST /titles/{title_id}/reviews/{review_id}/comments/ — список и
    создание (POST — только авторизованным).
    GET/PATCH/DELETE /titles/{title_id}/reviews/{review_id}/comments/{id}/ —
    чтение доступно всем, изменение и удаление — автору, модератору или
    админу.
    PUT не поддерживается.
    """

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
