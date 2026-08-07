# Lot G — Mode magasin / Scan V1

## Objectif

Ajouter une interface opérateur rapide sans remplacer les écrans de gestion.

Le scanner est traité comme un clavier USB/Bluetooth : il écrit une référence
puis envoie `Entrée`.

## Codes reconnus

- référence article `ART-xxxxxx` ;
- référence interne lot `LOT-xxxxxx` ;
- numéro de lot fournisseur ;
- recherche manuelle article si le résultat est unique.

Aucune nouvelle étiquette ni norme code-barres n’est imposée dans ce lot.
Le Lot J pourra générer des QR codes ou codes-barres contenant ces références.

## Interface

Nouveau menu :

```text
Mode magasin
```

Nouvelle route :

```text
/magasin
```

L’écran affiche immédiatement :

- article ou lot identifié ;
- stock physique ;
- stock réservé ;
- stock disponible ;
- répartition par emplacement ;
- date de péremption d’un lot béton.

Des gros raccourcis permettent ensuite d’aller vers :

- Préparations ;
- Retours ;
- Inventaires ;
- Stocks.

## Backend

Nouvel endpoint :

```text
GET /api/magasin/scan/{code}
```

## Migration

Aucune migration.

## Installation

```powershell
docker compose up --build -d backend frontend
```

Puis :

```text
Ctrl + F5
```

## Recette

1. Ouvrir `Mode magasin`.
2. Scanner ou saisir une référence article existante.
3. Appuyer sur Entrée.
4. Vérifier les stocks et emplacements.
5. Scanner `LOT-xxxxxx`.
6. Vérifier l’article, le numéro fournisseur, la péremption et les stocks lot.
7. Scanner directement un numéro de lot fournisseur.
8. Scanner une référence inconnue : message d’erreur attendu.
9. Vérifier qu’après chaque scan le focus revient dans le champ.

## Git

```powershell
git status
git add .
git commit -m "feat: add warehouse scan mode"
git push
```
