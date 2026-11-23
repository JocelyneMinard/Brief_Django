import csv
from ReadMe.models import Category
from tqdm import tqdm

def import_category(csv_path):
    created_count = 0
    updated_count = 0
    with open(csv_path, mode='r', encoding='utf-8') as file:
        rows = list(csv.DictReader(file, skipinitialspace=True))

        for row in tqdm(rows, desc="Import Categories", unit="category"):
            # Ignore row if empty
            if not row.get('id') or not row['id'].strip():
                continue
            update, created = Category.objects.update_or_create(
                id=int(row['id']),
                name=row['nom'],
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

    return created_count, updated_count

