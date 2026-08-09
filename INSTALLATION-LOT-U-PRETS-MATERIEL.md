# Lot U — Gestion des prêts de matériel

Migration `0035` après `0034`.

## Périmètre
Le Lot U s'appuie sur le référentiel `Matériels` existant, donc sur des
équipements individualisés `MAT-000001`, et non sur les articles consommables.

## Nouveau module
`Prêts matériel`

Fonctions :
- référence automatique `PRET-000001` ;
- choix du matériel disponible ;
- emprunteur COREF ;
- affaire facultative ;
- site / zone ;
- date de sortie et retour prévu ;
- emplacement et état au départ ;
- détection automatique des retards ;
- retour réel avec emplacement et état au retour ;
- historique complet.

Pendant un prêt, le matériel passe automatiquement à `EN_PRET`.
Au retour :
- `DISPONIBLE` : retour normal ;
- `EN_MAINTENANCE` : matériel à traiter ;
- `HORS_SERVICE` : matériel indisponible.

Une contrainte de base interdit deux prêts actifs simultanés sur le même
matériel.

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
`0035 (head)`

Puis `Ctrl + F5`.

## Recette
1. Ouvrir `Prêts matériel`.
2. Créer un prêt sur un matériel DISPONIBLE.
3. Vérifier son passage à EN_PRET dans Matériels.
4. Vérifier qu'il n'est plus proposé pour un second prêt.
5. Créer un prêt avec date de retour courte et vérifier le statut EN_RETARD après échéance.
6. Enregistrer le retour en DISPONIBLE.
7. Tester un retour EN_MAINTENANCE.
8. Vérifier l'historique.

## Git
```powershell
git status
git add .
git commit -m "feat: add equipment loan management"
git push
```
