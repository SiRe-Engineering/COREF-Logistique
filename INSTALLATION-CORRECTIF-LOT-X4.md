# Correctif Lot X.4 — Modèles ORM inventaire avancé

## Cause

X.3 avait renommé les classes Python mais le modèle livré conservait encore :

```text
campagnes_inventaire
lignes_inventaire
```

au lieu des tables créées par la migration 0038 :

```text
campagnes_inventaire_avance
lignes_inventaire_avance
```

Cela maintenait une collision avec le module Inventaires historique.

## Correction complète

Classes :

```text
CampagneInventaireAvance
LigneInventaireAvance
```

Tables :

```text
campagnes_inventaire_avance
lignes_inventaire_avance
```

Les relations SQLAlchemy utilisent désormais des chemins de classes qualifiés.

Aucune migration supplémentaire.
La base reste en `0038`.

## Installation

Extraire le correctif à la racine du projet puis :

```powershell
powershell -ExecutionPolicy Bypass -File .\APPLIQUER-ET-VERIFIER-X4.ps1
```

Attendu :

```text
campagnes_inventaire_avance lignes_inventaire_avance
MAPPERS SQLALCHEMY : OK
{"status":"ok","database":"connected",...}
0038 (head)
```

Ensuite :

```powershell
docker compose up --build -d frontend
```

puis `Ctrl + F5`.

Ne pas modifier PostgreSQL et ne pas utiliser `docker compose down -v`.
