from rest_framework import serializers
import re

from reviews.models import User


class SignupSerializer(serializers.Serializer):
    """Регистрация: email + username."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        if not re.fullmatch(r"[\w.@+-]+", value):
            raise serializers.ValidationError(
                "Username может содержать только буквы, цифры и @/./+/-/_."
            )
        return value

    def validate(self, data):
        username = data["username"]
        email = data["email"]

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError({"username": "Этот username уже занят."})
        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError({"email": "Этот email уже занят."})

        return data


class TokenSerializer(serializers.Serializer):
    """Получение токена: username + confirmation_code."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Для /users/ и /users/{username}/ — админ создаёт и смотрит."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class MeSerializer(serializers.ModelSerializer):
    """Для /users/me/ — свой профиль. Роль менять нельзя."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = ("role",)
