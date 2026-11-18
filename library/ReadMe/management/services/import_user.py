import csv
from pathlib import Path
from ReadMe.models import User
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()

def import_users_from_csv(file_path= None):
    """
    Fonction réutilisable pour importer les utilisateurs depuis un CSV.
    """
    # Si aucun chemin n'est fourni ou si c'est juste un nom de fichier / chemin relatif
    if file_path is None:
        file_path = settings.BASE_DIR / os.getenv('USERS_CSV', 'users_csv')
    else:
        path_obj = Path(file_path)
        if not path_obj.is_absolute():
            # Si le chemin commence par data/ ou contient déjà data/
            if 'data' in path_obj.parts:
                file_path = settings.BASE_DIR / path_obj
            else:
                # Sinon on force le placement dans le dossier data/
                file_path = settings.BASE_DIR / 'data' / path_obj

    count = 0
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_index, row in enumerate(reader, start=2): # start=2 pour inclure l'en-tête dans le compteur de lignes
                try:
                    user_id = int(row['id'])
                    first_name = row['prenom']
                    last_name = row['nom']
                    email = row['email']
                    role = row['role']
                    membership_number = row['numero_adherent']

                    # Générer un username unique (INDISPENSABLE pour django)
                    base_username = email.split('@')[0]
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                    # Vérifier les doublons avant création
                    if not User.objects.filter(email=email).exists() and not User.objects.filter(id=user_id).exists():
                        User.objects.create_user(
                            id=user_id,
                            username=username,       
                            email=email,
                            password="demo1234",     # Mot de passe temporaire
                            first_name=first_name,
                            last_name=last_name,
                            role=role,
                            membership_number=membership_number
                        )
                        count += 1
                        
                except KeyError as e:
                    print(f"Erreur de colonne manquante à la ligne {row_index}: clé {e} introuvable.")
                except ValueError as e:
                    print(f"Erreur de format de données à la ligne {row_index}: {e}")
                except Exception as e:
                    print(f"Erreur inattendue à la ligne {row_index}: {e}")

    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier '{file_path}' est introuvable. Vérifie le chemin.")
    except Exception as e:
        raise Exception(f"Erreur critique lors de l'ouverture du fichier CSV : {e}")
        
    return count

