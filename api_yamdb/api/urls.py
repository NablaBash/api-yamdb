from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    MeView,
    ReviewViewSet,
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
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)


urlpatterns = [
    path('v1/auth/signup/', SignupView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/users/', UserListCreateView.as_view()),
    path('v1/users/me/', MeView.as_view()),
    path('v1/users/<str:username>/', UserDetailView.as_view()),
    path('v1/', include(router.urls))
]
