# Correctif Lot X.3 — collision des classes SQLAlchemy

## Cause exacte

Le projet possède déjà un modèle historique :

`app.models.inventaire.LigneInventaire`

Le Lot X avait ajouté une seconde classe Python portant également le nom :

`LigneInventaire`

Même avec des noms de tables PostgreSQL différents, SQLAlchemy enregistre les
classes dans le même registre déclaratif. La relation :

`relationship("LigneInventaire")`

devenait donc ambiguë et faisait échouer la configuration de tous les mappers.

## Correction

Les classes du Lot X sont maintenant nommées :

- `CampagneInventaireAvance`
- `LigneInventaireAvance`

Les tables restent inchangées :

- `campagnes_inventaire_avance`
- `lignes_inventaire_avance`

Aucune migration supplémentaire. Alembic reste en `0038`.

## Installation

Extraire le correctif à la racine du projet, puis :

```powershell
powershell -ExecutionPolicy Bypass -File .\APPLIQUER-ET-VERIFIER-X3.ps1
```

Résultat attendu :

```text
MAPPERS SQLALCHEMY : OK
0038 (head)
```

`/api/auth/me` peut répondre `401 Unauthorized` sans session valide : c'est normal.
Il ne doit surtout plus répondre `500 Internal Server Error`.

Puis :

```powershell
docker compose up --build -d frontend
```

et `Ctrl + F5`.
