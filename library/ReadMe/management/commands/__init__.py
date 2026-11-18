from .import_book import ImportBook
from library.models import BaseCommand

# En faisant hériter la classe de BaseCommand, 
# Django reconnaît le fichier comme une commande officielle du projet, 
# au même titre que runserver ou migrate.
# python manage.py add_data

def add_data(BaseCommand):
    ImportBook()
    