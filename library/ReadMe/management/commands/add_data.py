# By having the class inherit from BaseCommand, 
# Django recognizes the file as an official command for the project, 
# just like runserver or migrate.
# python manage.py add_data

from django.core.management.base import BaseCommand
from ..services.import_book import import_books
from ..services.import_category import import_category
from ..services.import_user import import_users_from_csv
from ..services.import_reservation import import_reservation
import os
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Add data in database from csv file'

    def handle(self, *args, **options):
        counter = import_category(os.getenv('CATEGORIES_CSV', 'categories_csv'))
        counter += import_books(os.getenv('BOOKS_CSV', 'books_csv'))
        counter += import_users_from_csv()
        counter += import_reservation(os.getenv('RESERVATIONS_CSV', 'reservations_csv'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Importation réussie : {counter} objets traités.'
            )
        )
