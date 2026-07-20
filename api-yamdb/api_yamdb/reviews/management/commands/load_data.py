import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User

DATA_DIR = Path(settings.BASE_DIR) / 'static' / 'data'

MODELS_FILES = [
    (User, 'users.csv'),
    (Category, 'category.csv'),
    (Genre, 'genre.csv'),
    (Title, 'titles.csv'),
    (Review, 'review.csv'),
    (Comment, 'comments.csv'),
]

FK_FIELDS = {
    'category': Category,
    'author': User,
    'title_id': Title,
    'review_id': Review,
}


class Command(BaseCommand):
    """Загружает данные из CSV-файлов в базу данных."""

    help = 'Загрузка данных из CSV: python manage.py load_data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю загрузку данных...'))
        for model, filename in MODELS_FILES:
            self.load_model(model, filename)

        self.load_genre_title()

        self.stdout.write(self.style.WARNING('Все данные загружены!'))

    def load_model(self, model, filename):
        """Загружает данные из CSV в модель."""
        filepath = DATA_DIR / filename

        if not filepath.exists():
            self.stdout.write(
                self.style.WARNING(f'Файл {filename} не найден, пропускаю')
            )
            return

        with open(filepath, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            objects = []

            for row in reader:
                processed = {}
                for field, value in row.items():
                    if field in FK_FIELDS:
                        if field.endswith('_id'):
                            processed[field] = int(value)
                        else:
                            processed[f'{field}_id'] = int(value)
                    else:
                        processed[field] = value

                objects.append(model(**processed))

            model.objects.bulk_create(objects, ignore_conflicts=True)

        count = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'{model.__name__}: загружено записей — {count}'
            )
        )

    def load_genre_title(self):
        """Загружает M2M связь Genre-Title из genre_title.csv."""
        filepath = DATA_DIR / 'genre_title.csv'

        if not filepath.exists():
            self.stdout.write(
                self.style.WARNING('genre_title.csv не найден, пропускаю')
            )
            return

        with open(filepath, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                title = Title.objects.get(pk=int(row['title_id']))
                genre = Genre.objects.get(pk=int(row['genre_id']))
                title.genre.add(genre)

        self.stdout.write(
            self.style.SUCCESS('Genre ↔ Title (M2M): связи загружены')
        )
