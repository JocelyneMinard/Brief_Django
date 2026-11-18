import csv
from ReadMe.models import Category

def import_category(csv_path):
    counter = 0
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, skipinitialspace=True)

        for row in reader:
            # Ignore row if empty
            if not row.get('id') or not row['id'].strip():
                continue
            Category.objects.get_or_create(
                name=row['nom'],
            )
            counter += 1

    return counter
