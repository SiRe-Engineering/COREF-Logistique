# Correctif Lot X.2 — import backend Inventaires avancés

## Erreur corrigée

Le backend échouait après la migration 0038 sur :

```text
ModuleNotFoundError: No module named 'app.models.mouvement_stock'
```

Le Lot X importait le modèle depuis le mauvais module.

Correction :

```python
from app.models.mouvement import MouvementStock
```

Aucune nouvelle migration n'est nécessaire.
La base doit rester en `0038`.

## Installation

Extraire le ZIP à la racine de COREF Logistique en remplaçant le fichier existant.

Puis :

```powershell
powershell -ExecutionPolicy Bypass -File .\VERIFIER-LOT-X2.ps1
```

Le contrôle doit notamment afficher :

```text
IMPORT INVENTAIRES AVANCES : OK
```

et :

```text
0038 (head)
```

ainsi qu'un health backend OK.

Si le test d'import remonte une nouvelle erreur, conserver le log :
cela permettra de corriger le prochain symbole précisément sans toucher à la base.

Ne pas utiliser :

```powershell
docker compose down -v
```
