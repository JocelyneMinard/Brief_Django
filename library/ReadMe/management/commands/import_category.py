import csv
from ReadMe.models import Category



def import_category(csv_path='./data/categories.csv'):

    counter = 0

    with open(csv_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            Category.objects.get_or_create(
                name=row['nom'],
            )
            counter += 1

    return counter

