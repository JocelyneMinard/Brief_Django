# By having the class inherit from BaseCommand, 
# Django recognizes the file as an official command for the project, 
# just like runserver or migrate.
# python manage.py add_data

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction
from ..services.import_book import import_books
from ..services.import_category import import_category
from ..services.import_reservation import import_reservation
import os
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Add data in database from csv file'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                call_command("add_account_data")
                counter_cat, update_cat = import_category(os.getenv('CATEGORIES_CSV', 'categories_csv'))
                counter_book, update_book = import_books(os.getenv('BOOKS_CSV', 'books_csv'))
                counter_reservation, update_reservation = import_reservation(os.getenv('RESERVATIONS_CSV', 'reservations_csv'))

            self.stdout.write(
                self.style.SUCCESS(
                    f'Import successful: {counter_cat} categories created, {update_cat} categories updated.\n'
                    f'Import successful: {counter_book} books processed, {update_book} books updated.\n'
                    f'Import successful: {counter_reservation} reservation processed, {update_reservation} reservations updated.\n'
                )
            )
        except Exception as e:
            # CommandError show error on red inside terminal.
            raise CommandError(f"Import Failed. Détail : {e}")