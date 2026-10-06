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
