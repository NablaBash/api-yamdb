from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    MeView,
    SignupView,
    TokenView,
    UserDetailView,
    UserListCreateView,
)

router = DefaultRouter()

urlpatterns = [
    path("auth/signup/", SignupView.as_view()),
    path("auth/token/", TokenView.as_view()),
    path("users/", UserListCreateView.as_view()),
    path("users/me/", MeView.as_view()),
    path("users/<str:username>/", UserDetailView.as_view()),
] + router.urls
