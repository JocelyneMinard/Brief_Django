
from django.core.management.base import csv 
from library.models import Book
 
class ImportBook():
    help = 'Add data in database from csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_path',
            type = str,
            nargs = '?',
            default = './data/objets.csv',
            help = 'Path to csv file'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            counter = 0
            for row in reader:
                Book.objects.get_or_create(
                    tile = row['titre'],
                    author = row['autheur'],
                    published_year = row['annee'],
                    category_id = row['categorie_id'],
                    summary = row['resume'],
                    isbn = row['isbn'],
                    quantity = row['exemplaires'],
                )
                counter += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Importation réussie : {counter} objets traités.'
            )
        )