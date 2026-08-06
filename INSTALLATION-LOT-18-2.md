# Lot 18.2 — Ordre de préparation imprimable

## Périmètre strict

Ce lot ajoute :

- un bouton `Imprimer` dans la fiche Préparation ;
- une page dédiée à l’ordre de préparation ;
- une mise en page A4 paysage ;
- l’impression papier ou l’enregistrement PDF via le navigateur.

Ce lot ne modifie pas :

- la base de données ;
- les migrations Alembic ;
- les réservations ;
- le stock ;
- les mouvements ;
- les notifications ;
- l’expédition ;
- les statuts du lot 18.1.

## Contenu de l’ordre

- référence et nom de la préparation ;
- affaire, client, site et zone ;
- demandeur et préparateur ;
- date de besoin et fin prévue ;
- véhicule ;
- nombre de références ;
- nombre de lignes complètes, partielles et indisponibles ;
- article, lot et emplacement ;
- quantités demandées, préparées et manquantes ;
- observations et motifs d’écart ;
- cases de contrôle ;
- date, heure et signature du préparateur.

## Installation

Prérequis :

```text
Git : commit d67928f
Alembic : 0018
```

Copier le contenu de l’archive à la racine du projet, puis :

```powershell
docker compose up --build -d backend frontend
```

Aucune migration n’est attendue.

## Contrôles techniques

```powershell
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
curl.exe http://127.0.0.1:8000/api/health
```

Résultats attendus :

```text
Application startup complete
Ready
{"status":"ok","database":"connected","version":"1.0.0"}
```

## Checklist fonctionnelle

- [ ] Ouvrir une préparation.
- [ ] Vérifier la présence du bouton `Imprimer`.
- [ ] Cliquer sur `Imprimer`.
- [ ] Vérifier l’ouverture dans un nouvel onglet.
- [ ] Vérifier l’affaire, le client, le site et les acteurs.
- [ ] Vérifier chaque article, lot et emplacement.
- [ ] Vérifier les quantités demandées, préparées et manquantes.
- [ ] Vérifier les motifs des lignes partielles ou indisponibles.
- [ ] Cliquer sur `Imprimer / Enregistrer en PDF`.
- [ ] Vérifier le format A4 paysage dans l’aperçu.
- [ ] Vérifier que le bouton d’impression n’apparaît pas sur le document imprimé.
- [ ] Vérifier qu’aucune réservation ni aucun stock n’a changé.

## Commit uniquement après validation

```powershell
git status
git add .
git commit -m "feat: add printable preparation order"
git push
```
