from django.core.management.base import csv
from library.models import BaseCommand, Category


class Command(BaseCommand): 
    help = 'Importe les catégories à partir d’un fichier CSV'

    def add_arguments(self, parser): 
        parser.add_argument('csv_path', type=str, help='Le chemin vers le fichier CSV')

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        try:    
            with open(csv_path, mode='r', encoding='utf-8') as fichier:
                lecteur = csv.DictReader(fichier)

            compteur = 0
            for ligne in lecteur:
                Category.objects.get_or_create(
                    id=ligne['id'],
                    defaults={'cateogry': ligne['category']})
                compteur += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Importation réussie : {compteur} catégories traitées.'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error : {e}')
            )