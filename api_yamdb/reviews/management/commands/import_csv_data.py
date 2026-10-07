import csv

from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User


csv_to_models = {
    'category.csv': Category,
    'genre.csv': Genre,
    'titles.csv': Title,
    'users.csv': User,
    'genre_title.csv': Title.genre.through,
    'review.csv': Review,
    'comments.csv': Comment,
}


class Command(BaseCommand):
    help = 'Импорт данных из csv файлов в БД'

    def handle(self, *args, **options):
        for file_name, model in csv_to_models.items():
            with open('static/data/' + file_name, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if file_name == 'titles.csv':
                        row['category_id'] = row.pop('category')
                    elif file_name in ('review.csv', 'comments.csv'):
                        row['author_id'] = row.pop('author')
                    model.objects.get_or_create(**row)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Данные из файла {file_name} успешно загружены в БД!'
                )
            )
