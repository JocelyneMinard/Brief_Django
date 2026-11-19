# By having the class inherit from BaseCommand, 
# Django recognizes the file as an official command for the project, 
# just like runserver or migrate.
# python manage.py add_data

from django.core.management.base import BaseCommand
from django.core.management import call_command
from ..services.import_book import import_books
from ..services.import_category import import_category
from ..services.import_reservation import import_reservation
import os
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Add data in database from csv file'

    def handle(self, *args, **options):
        call_command("add_account_data")


        counter = import_category(os.getenv('CATEGORIES_CSV', 'categories_csv'))
        counter += import_books(os.getenv('BOOKS_CSV', 'books_csv'))
        counter += import_reservation(os.getenv('RESERVATIONS_CSV', 'reservations_csv'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Import successful: {counter} items processed.'
            )
        )
