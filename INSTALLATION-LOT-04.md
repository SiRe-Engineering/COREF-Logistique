# Lot 04 — Articles et référentiel

Ce lot :

- rattache les articles aux familles et sous-familles ;
- ajoute `GET /api/sous-familles?famille_id=...` ;
- génère automatiquement les références `ART-000001` ;
- ajoute les filtres famille et sous-famille aux articles.

## Installation

```powershell
docker compose down
```

Copier les fichiers du lot à la racine du dépôt, puis :

```powershell
docker compose up --build
```

Ne pas supprimer le volume PostgreSQL.

## Test Swagger

Créer un article sans champ `reference` :

```json
{
  "designation": "Béton dense test",
  "famille_id": 2,
  "sous_famille_id": 10,
  "unite": "sac",
  "stock_minimum": 5
}
```

La réponse doit contenir une référence automatique comme `ART-000001`.
