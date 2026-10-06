from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.constants import MAX_REVIEW_SCORE, MIN_REVIEW_SCORE


class User(AbstractUser):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLES = [
        (USER, "Пользователь"),
        (MODERATOR, "Модератор"),
        (ADMIN, "Администратор"),
    ]

    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name="Email",
    )
    bio = models.TextField(
        blank=True,
        verbose_name="Биография",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default=USER,
        verbose_name="Роль",
    )
    confirmation_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Код подтверждения",
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="titles",
    )
    genre = models.ManyToManyField(Genre, related_name="titles")

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name="Произведение",
        related_name="reviews",
    )
    text = models.TextField(
        verbose_name="Текст отзыва",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор отзыва",
        related_name="reviews",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Оценка произведения",
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                MIN_REVIEW_SCORE,
                message=f"Миниимальная оценка - {MIN_REVIEW_SCORE}",
            ),
            MaxValueValidator(
                MAX_REVIEW_SCORE,
                message=f"Максимальная оценка - {MAX_REVIEW_SCORE}",
            ),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации отзыва",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author"], name="unique_review"
            )
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    text = models.TextField(verbose_name="Текст комментария")
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время публикации комментария"
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
