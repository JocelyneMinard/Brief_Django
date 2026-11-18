import csv
from ReadMe.models import Book


def import_books(csv_path='./data/objets.csv'):
    counter = 0

    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            Book.objects.get_or_create(
                title=row['titre'],  # Correction de "tile" en "title"
                author=row['auteur'],
                published_year=row['annee'],
                category_id=row['categorie_id'],
                summary=row['resume'],
                isbn=row['isbn'],
                quantity=row['exemplaires'],
            )
            counter += 1

    return counter