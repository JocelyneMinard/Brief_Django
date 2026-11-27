import csv
from ReadMe.models import Reservation
from datetime import datetime
from tqdm import tqdm

def import_reservation(csv_path):
    created_count = 0
    updated_count = 0

    # utf-8-sig ignore invisible blank space inside file
    with open(csv_path, mode='r', encoding='utf-8-sig') as file:
        rows = list(csv.DictReader(file))
       
        for row in tqdm(rows, desc="Import Reservations", unit="reservation"):
            # Ignore row if empty
            if not row.get('id') or not row['id'].strip():
                continue

            update, created = Reservation.objects.update_or_create(
                id = int(row['id']), 
                defaults = {
                    'user_id': int(row['utilisateur_id']),
                    'book_id': int(row['objet_id']),
                    'status': row['etat'],
                    'creation_date': datetime.strptime(row["date_creation"], "%Y-%m-%d").date(),
                    'last_update': datetime.strptime(row["date_modification"], "%Y-%m-%d").date()
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

    return created_count, updated_count

