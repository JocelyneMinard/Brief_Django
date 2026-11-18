# En faisant hériter la classe de BaseCommand, 
# Django reconnaît le fichier comme une commande officielle du projet, 
# au même titre que runserver ou migrate.
# python manage.py add_data

from django.core.management.base import BaseCommand
from ..services.import_book import import_books
from ..services.import_category import import_category
from ..services.import_user import import_users_from_csv

class Command(BaseCommand):
    help = 'Add data in database from csv file'

    def handle(self, *args, **options):
        counter = import_category("./data/categories.csv")
        counter = import_books("./data/objets.csv")
        counter = import_users_from_csv()

        self.stdout.write(
            self.style.SUCCESS(
                f'Importation réussie : {counter} objets traités.'
            )
        )
