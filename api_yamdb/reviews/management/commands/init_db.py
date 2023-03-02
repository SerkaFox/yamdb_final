import csv

from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, User

MODELS_DATA = {
    Category: 'static/data/category.csv',
    Genre: 'static/data/genre.csv',
    Title: 'static/data/titles.csv',
    User: 'static/data/users.csv.old',
    Review: 'static/data/review.csv',
    Comment: 'static/data/comments.csv',
}
MANY_TO_MANY = 'static/data/genre_title.csv'


class Command(BaseCommand):
    help = 'Import database from csv files'

    def handle(self, *args, **options):

        for model, data in MODELS_DATA.items():
            model.objects.all().delete()
            with open(data, encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=",")
                print(reader)
                for row in reader:
                    print(row)
                    model.objects.get_or_create(**row)
            file.close()
        with open(MANY_TO_MANY, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(reader)
            for row in reader:
                print(row)
                title = Title.objects.get(id=int(row['title_id']))
                title.genre.add(row['genre_id'])
