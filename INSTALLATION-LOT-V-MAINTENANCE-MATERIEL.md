# Lot V — Maintenance & contrôles du matériel

Migration `0036` après `0035`.

## Nouveau module
`Maintenance matériel`

Fonctions :
- intervention `MAINT-000001` ;
- préventif, correctif, contrôle périodique, étalonnage, autre ;
- planification ;
- diagnostic ;
- action réalisée ;
- prestataire ;
- coût HT ;
- prochaine échéance de contrôle ;
- dashboard des contrôles en retard et à 30 jours.

## Synchronisation matériel
Lors du passage d'une intervention à `EN_COURS`, le matériel passe
automatiquement à `EN_MAINTENANCE`.

Lors de la fin :
`EN_MAINTENANCE → DISPONIBLE`.

Une action réalisée est obligatoire pour terminer une intervention.

Un matériel actuellement `EN_PRET / En déplacement` ne peut pas démarrer une
maintenance corrective, un contrôle ou un étalonnage avant son retour.

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
`0036 (head)`

Puis `Ctrl + F5`.

## Recette
1. Créer une intervention préventive.
2. La passer EN_COURS : le matériel doit passer EN_MAINTENANCE.
3. Saisir diagnostic et action réalisée.
4. Terminer l'intervention avec une prochaine date de contrôle.
5. Vérifier retour du matériel à DISPONIBLE.
6. Vérifier l'échéance dans le dashboard.
7. Tester une intervention corrective sur un matériel En déplacement : elle doit être refusée avant retour.
