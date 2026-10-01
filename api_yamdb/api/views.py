import random

from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, User
from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    MeSerializer,
    ReadTitleSerializer,
    SignupSerializer,
    TokenSerializer,
    UserSerializer,
    WriteTitleSerializer,
)


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
    lookup_url_kwarg = 'titles_id'
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadTitleSerializer
        return WriteTitleSerializer


class SignupView(APIView):
    """POST /auth/signup/ — регистрация, отправка кода на email."""

    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]

        user, _ = User.objects.get_or_create(
            username=username,
            email=email,
        )

        confirmation_code = str(random.randint(100000, 999999))
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            subject="YaMDb confirmation code",
            message=f"Your confirmation code: {confirmation_code}",
            from_email="noreply@yamdb.fake",
            recipient_list=[email],
        )

        return Response(
            {"email": email, "username": username},
            status=status.HTTP_200_OK,
        )


class TokenView(APIView):
    """POST /auth/token/ — получить JWT по username и коду."""

    permission_classes = []

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        code = serializer.validated_data["confirmation_code"]

        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.confirmation_code != code:
            return Response(
                {"confirmation_code": ["Неверный код подтверждения."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)


class UserListCreateView(generics.ListCreateAPIView):
    """GET/POST /users/ — только админ."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ["username"]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /users/{username}/ — только админ."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = "username"
    http_method_names = ["get", "patch", "delete"]


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /users/me/ — свой профиль."""

    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]

    def get_object(self):
        return self.request.user
