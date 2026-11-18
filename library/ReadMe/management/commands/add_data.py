# En faisant hériter la classe de BaseCommand, 
# Django reconnaît le fichier comme une commande officielle du projet, 
# au même titre que runserver ou migrate.
# python manage.py add_data

from django.core.management.base import BaseCommand
from .import_book import import_books
from .import_category import import_category

class Command(BaseCommand):
    help = 'Add data in database from csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_path',
            type=str,
            nargs='?',
            default='./data/objets.csv',
            help='Path to csv file'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        counter = import_category(csv_path)
        counter = import_books(csv_path)

        self.stdout.write(
            self.style.SUCCESS(
                f'Importation réussie : {counter} objets traités.'
            )
        )
