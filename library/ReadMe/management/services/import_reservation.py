import csv
from ReadMe.models import Reservation
from datetime import datetime

def import_reservation(csv_path):
    counter = 0

    # utf-8-sig ignore invisible blank space inside file
    with open(csv_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Ignore row if empty
            if not row.get('id') or not row['id'].strip():
                continue

            Reservation.objects.get_or_create(
                user_id = int(row['utilisateur_id']),
                book_id = int(row['objet_id']),
                status = row['etat'],
                creation_date = datetime.strptime(row["date_creation"], "%Y-%m-%d").date(),
                last_update = datetime.strptime(row["date_modification"], "%Y-%m-%d").date()
            )
            counter += 1

    return counter
