# Lot J — Documents, étiquettes et QR codes

## Fonctions ajoutées

### Articles

Depuis la fiche article :

```text
Imprimer l’étiquette QR
```

Format :

```text
90 × 50 mm
```

Le QR contient exactement la référence article déjà reconnue par le
`Mode magasin`.

### Lots béton

Une action d’impression est disponible directement dans la liste.

L’étiquette contient :

- référence interne ;
- article ;
- numéro de lot fournisseur ;
- fabrication ;
- péremption ;
- fournisseur ;
- QR code.

Le QR contient la `reference_interne` du lot.

### Préparations / Retours

Trois documents sont disponibles :

```text
Ordre de préparation
Bon d’expédition
Fiche de retour chantier
```

Les documents sont conçus pour impression A4 paysage / export PDF navigateur.

### Inventaires

La fiche d’inventaire est imprimable avec :

- article ;
- lot ;
- emplacement ;
- quantité théorique ;
- quantité comptée ;
- écart ;
- observations ;
- zone de validation.

## QR code

Le QR est généré localement par le backend :

```text
GET /api/documents/qrcode.svg?value=ART-000001
```

Aucun service Internet, CDN ou logiciel d’étiquetage externe n’est utilisé.

Les QR du Lot J sont volontairement limités aux références internes courtes
déjà générées par COREF Logistique.

## Base de données

Aucune migration.

## Installation

```powershell
docker compose down
docker compose up --build -d
```

Puis :

```powershell
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Faire ensuite :

```text
Ctrl + F5
```

## Recette

1. Articles → ouvrir un article → `Imprimer l’étiquette QR`.
2. Scanner le QR avec un scanner USB/Bluetooth dans `Mode magasin`.
3. Lots béton → imprimer une étiquette → scanner le QR.
4. Préparations/Retours → ouvrir une préparation :
   - ordre de préparation ;
   - bon d’expédition ;
   - fiche de retour.
5. Inventaires → ouvrir un inventaire → imprimer la fiche.
6. Tester `Imprimer / Enregistrer en PDF` dans le navigateur.

## Git

```powershell
git status
git add .
git commit -m "feat: add printable logistics documents and qr labels"
git push
```
