from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    MeView,
    SignupView,
    TitleViewSet,
    TokenView,
    UserDetailView,
    UserListCreateView,
)


router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)


urlpatterns = [
    path('auth/signup/', SignupView.as_view()),
    path('auth/token/', TokenView.as_view()),
    path('users/', UserListCreateView.as_view()),
    path('users/me/', MeView.as_view()),
    path('users/<str:username>/', UserDetailView.as_view()),
    path('', include(router.urls))
]
