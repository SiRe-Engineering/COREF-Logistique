# Lot Q — Documents fournisseurs & traçabilité qualité

## Migration

`0031` après `0030`.

## Nouveautés

Nouveau module :

`Qualité / Documents fournisseurs`

Documents acceptés :
- certificat fournisseur ;
- FDS ;
- fiche technique ;
- bon de livraison ;
- autre.

Formats :
- PDF ;
- PNG ;
- JPG/JPEG ;
- WEBP.

Taille maximale : 15 Mo par fichier.

Les fichiers sont conservés directement en base PostgreSQL. Ils ne sont donc
pas perdus lors d'un rebuild Docker et ne nécessitent pas de volume fichier
supplémentaire.

## Béton

Pour un lot Béton, la conformité documentaire exige :
- un CERTIFICAT ;
- une FDS.

Statuts :
- COMPLET ;
- INCOMPLET ;
- EXPIRE.

Lors du dépôt d'un certificat ou d'une FDS, les anciens champs
`certificat_reference` / `fds_reference` du lot sont également maintenus pour
compatibilité avec les écrans existants.

## Installation

```powershell
docker compose down
docker compose up --build -d
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Ne pas utiliser `-v`.

Attendu :

`0031 (head)`

Puis `Ctrl + F5`.

## Recette

1. Ouvrir Lots béton.
2. Cliquer Documents fournisseurs.
3. Déposer un certificat PDF sur un lot.
4. Déposer une FDS sur le même lot.
5. Vérifier le passage INCOMPLET → COMPLET.
6. Ouvrir les documents.
7. Tester un document avec date d'expiration passée.
8. Vérifier le statut EXPIRE.
9. Supprimer un certificat et vérifier le retour à INCOMPLET.

## Git

```powershell
git status
git add .
git commit -m "feat: add supplier quality documents"
git push
```
