#!/usr/bin/env python
"""Vérifie la cohérence du jeu de données « bibliothèque de quartier ».

Usage : python verifier_donnees.py [dossier]
Sans argument, le dossier du script est utilisé.
Code de retour : 0 si tout est cohérent, 1 sinon.
"""

import sys
from pathlib import Path

import pandas as pd

COLONNES = {
    "categories.csv": ["id", "nom"],
    "objets.csv": ["id", "titre", "auteur", "annee", "categorie_id", "resume", "exemplaires", "isbn"],
    "utilisateurs.csv": ["id", "prenom", "nom", "email", "role", "numero_adherent"],
    "actions.csv": ["id", "utilisateur_id", "objet_id", "etat", "date_creation", "date_modification"],
}
ETATS = {"en_attente", "prete", "empruntee", "rendue", "annulee"}
ETATS_ACTIFS = {"en_attente", "prete", "empruntee"}
ROLES = {"utilisateur", "gestionnaire"}
DATE_MIN, DATE_MAX = pd.Timestamp("2026-09-01"), pd.Timestamp("2026-11-15")

erreurs = []


def ok(message):
    print(f"✓ {message}")


def controle(condition, message, detail=""):
    if condition:
        ok(message)
    else:
        erreurs.append(f"{message}{' : ' + detail if detail else ''}")


def cle_isbn13(douze):
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(douze))
    return str((10 - total % 10) % 10)


def main(dossier):
    dossier = Path(dossier)

    # 1. Présence des fichiers
    manquants = [n for n in COLONNES if not (dossier / n).exists()]
    controle(not manquants, "Fichiers présents", ", ".join(manquants))
    if manquants:
        return

    tables = {n: pd.read_csv(dossier / n, dtype=str, keep_default_na=False) for n in COLONNES}

    # 2. Colonnes exactes
    for nom, attendu in COLONNES.items():
        controle(list(tables[nom].columns) == attendu,
                 f"Colonnes de {nom}", f"trouvé {list(tables[nom].columns)}")

    cat, obj, usr, act = (tables["categories.csv"], tables["objets.csv"],
                          tables["utilisateurs.csv"], tables["actions.csv"])

    # 3. Identifiants entiers, uniques, à partir de 1
    for nom, df in tables.items():
        ids = pd.to_numeric(df["id"], errors="coerce")
        controle(ids.notna().all() and ids.is_unique and ids.min() == 1
                 and set(ids.astype(int)) == set(range(1, len(df) + 1)),
                 f"Identifiants de {nom} entiers, uniques et consécutifs à partir de 1")

    # 4. Effectifs
    controle(len(cat) == 12, "12 catégories", f"{len(cat)}")
    controle(len(obj) == 300, "300 livres", f"{len(obj)}")
    controle(len(usr) == 20, "20 utilisateurs", f"{len(usr)}")
    controle(len(act) == 60, "60 réservations", f"{len(act)}")

    # 5. Catégories
    controle(cat["nom"].is_unique and (cat["nom"].str.strip() != "").all(), "Noms de catégories non vides et uniques")

    # 6. Livres
    annee = pd.to_numeric(obj["annee"], errors="coerce")
    controle(annee.notna().all() and annee.between(1850, 2025).all(), "Années entre 1850 et 2025")
    ex = pd.to_numeric(obj["exemplaires"], errors="coerce")
    controle(ex.notna().all() and ex.between(1, 4).all(), "Exemplaires entre 1 et 4")
    controle(obj["categorie_id"].isin(set(cat["id"])).all(), "Clé étrangère objets.categorie_id → categories.id")
    controle(obj["titre"].is_unique and (obj["titre"].str.strip() != "").all(), "Titres non vides et uniques")
    controle((obj["auteur"].str.strip() != "").all(), "Auteurs non vides")
    controle(obj["resume"].str.count(r"[.!?»]\s|[.!?»]$").ge(2).all(), "Résumés d'au moins deux phrases")
    isbn_ok = obj["isbn"].str.fullmatch(r"978\d{10}").fillna(False)
    cle_ok = obj["isbn"].apply(lambda s: len(s) == 13 and s[-1] == cle_isbn13(s[:12]))
    controle(isbn_ok.all() and cle_ok.all() and obj["isbn"].is_unique,
             "ISBN à 13 chiffres (préfixe 978, clé de contrôle correcte, uniques)")

    # 7. Utilisateurs
    controle(usr["email"].is_unique, "E-mails uniques")
    controle(usr["email"].str.fullmatch(r"[a-z]+\.[a-z]+@exemple\.fr").all(),
             "E-mails au format prenom.nom@exemple.fr sans accent")
    controle(usr["role"].isin(ROLES).all(), "Rôles valides")
    controle((usr["role"] == "gestionnaire").sum() == 2 and (usr["role"] == "utilisateur").sum() == 18,
             "18 utilisateurs et 2 gestionnaires")
    controle(usr["numero_adherent"].is_unique and usr["numero_adherent"].str.fullmatch(r"BIB-\d{4}").all(),
             "Numéros d'adhérent au format BIB-0001, uniques")

    # 8. Réservations
    controle(act["utilisateur_id"].isin(set(usr["id"])).all(), "Clé étrangère actions.utilisateur_id → utilisateurs.id")
    controle(act["objet_id"].isin(set(obj["id"])).all(), "Clé étrangère actions.objet_id → objets.id")
    controle(act["etat"].isin(ETATS).all(), "États valides")
    d1 = pd.to_datetime(act["date_creation"], format="%Y-%m-%d", errors="coerce")
    d2 = pd.to_datetime(act["date_modification"], format="%Y-%m-%d", errors="coerce")
    controle(d1.notna().all() and d2.notna().all(), "Dates au format ISO AAAA-MM-JJ")
    controle(d1.between(DATE_MIN, DATE_MAX).all() and d2.between(DATE_MIN, DATE_MAX).all(),
             "Dates entre 2026-09-01 et 2026-11-15")
    controle((d2 >= d1).all(), "date_modification postérieure ou égale à date_creation")

    roles = usr.set_index("id")["role"]
    controle((act["utilisateur_id"].map(roles) == "utilisateur").all(),
             "Seuls les utilisateurs de rôle « utilisateur » réservent")

    actives = act[act["etat"].isin(ETATS_ACTIFS)]
    par_livre = actives.groupby("objet_id").size()
    stock = obj.set_index("id")["exemplaires"].astype(int)
    depassements = par_livre[par_livre > stock.reindex(par_livre.index)]
    controle(depassements.empty, "Réservations actives ≤ exemplaires pour chaque livre",
             f"livres {list(depassements.index)}")
    par_user = actives.groupby("utilisateur_id").size()
    controle((par_user <= 3).all(), "Au plus 3 réservations actives par adhérent",
             f"utilisateurs {list(par_user[par_user > 3].index)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent)
    if erreurs:
        print("\nErreurs détectées :")
        for e in erreurs:
            print(f"  - {e}")
        sys.exit(1)
    print("\nDonnées cohérentes.")
    sys.exit(0)
