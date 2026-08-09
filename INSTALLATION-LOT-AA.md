# Installation — Lot AA Consolidation V1

Extraire le ZIP à la racine du projet en remplaçant les fichiers proposés.

Puis :

```powershell
powershell -ExecutionPolicy Bypass -File .\APPLIQUER-ET-VERIFIER-LOT-AA.ps1
```

Attendu :

```text
0038 (head)
MAPPERS : OK
```

Le health doit répondre `200 OK`.
Le test `/api/articles` sans jeton doit désormais répondre `401 Unauthorized` : c'est volontaire et confirme que l'API métier est protégée.

Ensuite ouvrir `http://localhost:3000`, se connecter normalement et vérifier :
- dashboard ;
- articles ;
- stocks ;
- achats ;
- préparations ;
- matériels ;
- inventaires ;
- alertes.

Aucune migration et aucun `docker compose down -v`.
