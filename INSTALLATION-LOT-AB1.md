# Lot AB.1 — Fiabilisation des tests

Ce lot ne modifie aucun fichier applicatif, aucune migration et aucune donnée.

## Pourquoi

Le premier audit AB a remonté de nombreuses erreurs ayant la même origine :

```text
ModuleNotFoundError: No module named 'app'
```

Avant de modifier les tests ou l'application, AB.1 exécute Pytest explicitement
depuis `/app` via le même interpréteur Python que le backend :

```text
cd /app && python -m pytest
```

Cela permet de distinguer :

1. un problème réel de chemin/import ;
2. des tests obsolètes ;
3. de vrais défauts applicatifs.

## Exécution

Extraire ce ZIP à la racine de COREF Logistique puis lancer :

```powershell
powershell -ExecutionPolicy Bypass -File .\TESTER-LOT-AB1.ps1
```

Le script crée :

```text
AB1-PYTEST-COLLECT.txt
AB1-PYTEST-RESULTATS.txt
```

Envoyer ensuite la sortie PowerShell ou les deux fichiers.

## Important

AB.1 est volontairement diagnostic :
- aucun changement de sécurité ;
- aucun changement frontend ;
- aucune migration Alembic ;
- aucun commit Git automatique.
