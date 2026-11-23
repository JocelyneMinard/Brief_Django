import csv
from pathlib import Path
from django.contrib.auth import get_user_model
from django.conf import settings
import os
from dotenv import load_dotenv

User = get_user_model()

load_dotenv()

def import_users_from_csv(file_path= None)-> None:
    """
    Reusable function for importing users from a CSV file.
    Searches for the desired file using a specified path or the default path.
    Then prepares each data point to match the desired column.
    Adds a username, which is required.
    Then checks for duplicates.

    If even a single error occurs, the entire process is canceled.

    [Args]:
    file_path : path of the csv file
    """

    # If no path is provided, or if it is just a filename or relative path
    if file_path is None:
        file_path = settings.BASE_DIR / os.getenv('USERS_CSV', 'users_csv')

    else:

        path_obj = Path(file_path)
        if not path_obj.is_absolute():

            # If the path begins with “data/” or already contains “data/”
            if 'data' in path_obj.parts:
                file_path = settings.BASE_DIR / path_obj

            else:
                # Otherwise, we force the file to be placed in the data/ folder.
                file_path = settings.BASE_DIR / 'data' / path_obj

    count = 0
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # start=2 to include the header in the line count
            for row_index, row in enumerate(reader, start=2): 
                try:
                    user_id = int(row['id'])
                    first_name = row['prenom']
                    last_name = row['nom']
                    email = row['email']
                    role = row['role']
                    membership_number = row['numero_adherent']

                    if not User.objects.filter(email=email).exists() and not User.objects.filter(id=user_id).exists():
                        User.objects.create_user(
                            id=user_id,   
                            email=email,
                            password="demo1234",     # Temporary Password
                            first_name=first_name,
                            last_name=last_name,
                            role=role,
                            membership_number=membership_number
                        )
                        count += 1
                        
                except KeyError as e:
                    print(f"Missing column error at row {row_index}: key {e} not found.")
                except ValueError as e:
                    print(f"Data format error in row {row_index}: {e}")
                except Exception as e:
                    print(f"Unexpected error on line {row_index}: {e}")

    except FileNotFoundError:
        raise FileNotFoundError(f"The file ‘{file_path}’ cannot be found. Check the path.")
    except Exception as e:
        raise Exception(f"Critical error while opening the CSV file: {e}")
        
    return count

