# Jeu de données « Bibliothèque de quartier »

Jeu de données fictif destiné au brief Django. Toutes les données sont inventées et générées localement par `generer.py` (graine fixe : 42). Les quelques classiques du domaine public présents dans `objets.csv` sont attribués à leur auteur réel ; tous les autres titres, auteurs, personnes et adresses sont imaginaires.

Les fichiers sont des CSV encodés en UTF-8, séparateur virgule, avec ligne d'en-tête. Les identifiants sont des entiers consécutifs à partir de 1.

## Fichiers

| Fichier | Lignes | Contenu |
|---|---|---|
| `categories.csv` | 12 | Genres littéraires |
| `objets.csv` | 300 | Livres du fonds |
| `utilisateurs.csv` | 20 | Comptes (adhérents et gestionnaires) |
| `actions.csv` | 60 | Réservations |
| `generer.py` | — | Script de génération (à relancer pour reproduire les fichiers à l'identique) |
| `verifier_donnees.py` | — | Script de contrôle de cohérence |

### `categories.csv`

| Colonne | Type | Description |
|---|---|---|
| `id` | entier | Identifiant de la catégorie |
| `nom` | texte | Nom du genre (roman, policier, science-fiction, fantasy, jeunesse, bande dessinée, biographie, histoire, sciences, cuisine, voyage, poésie) |

### `objets.csv`

| Colonne | Type | Description |
|---|---|---|
| `id` | entier | Identifiant du livre |
| `titre` | texte | Titre, unique dans le fonds |
| `auteur` | texte | Prénom et nom de l'auteur |
| `annee` | entier | Année de publication, entre 1850 et 2025 |
| `categorie_id` | entier | Référence vers `categories.id` |
| `resume` | texte | Résumé en deux phrases |
| `exemplaires` | entier | Nombre d'exemplaires possédés, entre 1 et 4 |
| `isbn` | texte | ISBN à 13 chiffres (préfixe 978, clé de contrôle valide). À stocker en texte, jamais en entier. |

### `utilisateurs.csv`

| Colonne | Type | Description |
|---|---|---|
| `id` | entier | Identifiant du compte |
| `prenom` | texte | Prénom |
| `nom` | texte | Nom de famille |
| `email` | texte | Adresse au format `prenom.nom@exemple.fr`, sans accent, unique |
| `role` | texte | `utilisateur` (18 comptes) ou `gestionnaire` (2 comptes) |
| `numero_adherent` | texte | Numéro de carte au format `BIB-0001`, unique |

Le fichier ne contient pas de mot de passe : le brief impose le mot de passe `demo1234` pour tous les comptes, à hacher lors du chargement.

### `actions.csv`

| Colonne | Type | Description |
|---|---|---|
| `id` | entier | Identifiant de la réservation |
| `utilisateur_id` | entier | Référence vers `utilisateurs.id` (toujours un compte de rôle `utilisateur`) |
| `objet_id` | entier | Référence vers `objets.id` |
| `etat` | texte | État courant, voir ci-dessous |
| `date_creation` | date ISO `AAAA-MM-JJ` | Date de la demande, entre le 2026-09-01 et le 2026-11-15 |
| `date_modification` | date ISO `AAAA-MM-JJ` | Date du dernier changement d'état, postérieure ou égale à `date_creation` |

## États et transitions

| État | Signification | Compte comme active ? |
|---|---|---|
| `en_attente` | Demande déposée, non encore traitée | oui |
| `prete` | Livre mis de côté, l'adhérent peut venir le retirer | oui |
| `empruntee` | Livre retiré par l'adhérent | oui |
| `rendue` | Livre restitué, réservation close | non |
| `annulee` | Réservation abandonnée avant le retrait | non |

Transitions autorisées :

- `en_attente` → `prete` → `empruntee` → `rendue` (parcours nominal) ;
- `en_attente` → `annulee` et `prete` → `annulee` (annulation, par l'adhérent ou par un gestionnaire) ;
- aucune autre transition n'est permise : une réservation `empruntee` ne peut pas être annulée, et `rendue` comme `annulee` sont des états finaux.

Répartition dans le jeu de données : 36 rendues, 8 annulées, 7 empruntées, 4 prêtes, 5 en attente.

## Règles métier

Ces règles sont respectées par les données livrées et doivent être garanties par l'application lors de toute création ou changement d'état :

1. **Disponibilité** : pour un livre donné, le nombre de réservations actives (`en_attente`, `prete`, `empruntee`) ne dépasse jamais son nombre d'`exemplaires`.
2. **Plafond par adhérent** : un adhérent ne détient jamais plus de trois réservations actives simultanément.
3. **Qui réserve** : seuls les comptes de rôle `utilisateur` réservent ; les gestionnaires traitent les réservations mais n'en créent pas pour eux-mêmes.

## Exemple de commande `charger_donnees`

La commande de gestion Django `charger_donnees` (fichier `management/commands/charger_donnees.py`) importe les quatre fichiers dans l'ordre imposé par les clés étrangères :

1. **Catégories** : lecture de `categories.csv`, création ou mise à jour de chaque catégorie à partir de son `id`.
2. **Objets** : lecture de `objets.csv`, rattachement de chaque livre à sa catégorie via `categorie_id`, conservation de l'ISBN sous forme de chaîne.
3. **Utilisateurs** : lecture de `utilisateurs.csv`, création ou mise à jour des comptes avec prénom, nom, e-mail, rôle et numéro d'adhérent ; le mot de passe `demo1234` est attribué à chaque compte par `set_password` (jamais stocké en clair), et l'e-mail sert d'identifiant de connexion.
4. **Actions** : lecture de `actions.csv`, création ou mise à jour des réservations avec leurs références vers l'utilisateur et le livre, leur état et leurs deux dates.

La commande est rejouable : chaque ligne est traitée avec `update_or_create` en utilisant l'identifiant du CSV comme clé de recherche, de sorte qu'une seconde exécution met à jour les enregistrements existants sans créer de doublons. Le chemin du dossier contenant les CSV est passé en argument (avec une valeur par défaut pointant vers ce dossier), et la commande affiche en fin d'exécution le nombre de lignes traitées par fichier. Il est recommandé d'envelopper l'ensemble dans une transaction afin qu'une erreur de lecture laisse la base dans son état initial.

## Vérification

```
python verifier_donnees.py
```

Le script contrôle la présence des fichiers, les colonnes, les clés étrangères, l'unicité des identifiants et des e-mails, les règles métier, les états et les dates. Il affiche une ligne `✓` par contrôle réussi et se termine par « Données cohérentes. » (code de retour 0) ou par la liste des erreurs (code de retour 1).
