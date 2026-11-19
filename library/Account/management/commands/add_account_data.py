# By having the class inherit from BaseCommand, 
# Django recognizes the file as an official command for the project, 
# just like runserver or migrate.
# python manage.py add_data

from django.core.management.base import BaseCommand
from Account.management.services.import_user import import_users_from_csv

import os
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Add data in database from csv file'

    def handle(self, *args, **options):
        counter = 0
        counter += import_users_from_csv()

        self.stdout.write(
            self.style.SUCCESS(
                f'Import successful: {counter} users processed.'
            )
        )