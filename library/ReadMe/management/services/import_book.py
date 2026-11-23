import csv
from ReadMe.models import Book
from tqdm import tqdm

def import_books(csv_path):
    created_count = 0
    updated_count = 0
    
    with open(csv_path, mode='r', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))

        for row in tqdm(rows, desc="Import Books", unit="book"):
            # Ignore row if empty
            if not row.get('id') or not row['id'].strip():
                continue
            update, created = Book.objects.update_or_create(
                id=int(row['id']), # Ou isbn=row['isbn']
                defaults = {
                    'title': row['titre'], 
                    'author': row['auteur'],
                    'published_year': row['annee'],
                    'category_id': row['categorie_id'],
                    'summary': row['resume'],
                    'isbn': row['isbn'],
                    'quantity': row['exemplaires'],
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

    return created_count, updated_count