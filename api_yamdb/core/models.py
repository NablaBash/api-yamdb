from django.conf import settings
from django.db import models


class NameAndSlug(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class AuthorText(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ['-pub_date']
