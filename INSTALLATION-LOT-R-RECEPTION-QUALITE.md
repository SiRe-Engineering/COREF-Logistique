# Lot R — Réception fournisseur enrichie & contrôle qualité

## Migration
`0032` après `0031`.

## Réception fournisseur
La fenêtre de réception ajoute :
- référence du bon de livraison ;
- fichier BL PDF/image ;
- contrôle visuel : Conforme / Sous réserve / Non conforme ;
- commentaire de réserve obligatoire si nécessaire ;
- commentaire qualité ;
- sélection du lot béton dans une liste plutôt que saisie d'un ID.

## Béton
Le backend vérifie automatiquement la présence d'une FDS sur le lot béton.

La FDS manquante ne bloque pas physiquement l'entrée en stock, mais la réception
est enregistrée avec le statut `A_CONTROLER` et un avertissement immédiat.

Cela évite de perdre une livraison physiquement reçue tout en conservant une
non-conformité documentaire visible.

## Bon de livraison
Si un fichier BL est joint à la réception, il est enregistré dans le module
Documents fournisseurs et relié à :
- la commande ;
- le fournisseur ;
- l'article ;
- le lot béton s'il existe.

## Contrôle réception
Nouvelle page :
`Fournisseurs / Achats → Contrôles réception`

Elle affiche l'historique des réceptions avec BL, FDS, qualité et réserves.

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

Attendu : `0032 (head)`.

Puis `Ctrl + F5`.

## Recette
1. Réceptionner un article non béton conforme avec un BL.
2. Vérifier stock/CUMP + Contrôles réception + document BL.
3. Réceptionner un article sous réserve et vérifier commentaire obligatoire.
4. Pour un béton avec FDS : réception CONFORME.
5. Pour un béton sans FDS : entrée stock autorisée mais statut A_CONTROLER et avertissement.
6. Vérifier le lot et le BL dans Documents fournisseurs.

## Git
```powershell
git status
git add .
git commit -m "feat: add supplier receipt quality controls"
git push
```
