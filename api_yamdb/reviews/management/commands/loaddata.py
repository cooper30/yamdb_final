import csv

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

LIST = {
    User: 'users.csv',
    Genre: 'genre.csv',
    Category: 'category.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv'
}

ALREADY_LOADED_ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = "Loads data from fixture"

    def handle(self, *args, **options):
        # Проверим если существует хотя бы один пользователь, то ошибка
        if Genre.objects.exists():
            print('Data already loaded...exiting.')
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return

        for model, csv_f in LIST.items():
            with open(
                    f'{settings.BASE_DIR}/static/data/{csv_f}',
                    'r',
                    encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                if model in (User, Category, Genre):
                    model.objects.bulk_create(model(**data) for data in reader)
                else:
                    for row in reader:
                        if model == Title:
                            Title(
                                id=row['id'],
                                name=row['name'],
                                year=row['year'],
                                category=Category.objects.get(
                                    pk=row['category']),
                            ).save()

                        elif model == Review:
                            Review(
                                id=row['id'],
                                title=Title.objects.get(pk=row['title_id']),
                                text=row['text'],
                                author=User.objects.get(pk=row['author']),
                                score=row['score'],
                                pub_date=row['pub_date'],
                            ).save()

                        elif model == Comment:
                            Comment(
                                id=row['id'],
                                review=Review.objects.get(pk=row['review_id']),
                                text=row['text'],
                                author=User.objects.get(pk=row['author']),
                                pub_date=row['pub_date']
                            ).save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Loads data {model.__name__} is success'
                    )
                )
        self.stdout.write(self.style.SUCCESS('Data loading completed'))
