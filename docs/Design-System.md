# Design System — COREF Logistique V2

## 1. Objectif

Le Design System garantit une ergonomie uniforme dans tous les modules :

- Articles ;
- Stocks ;
- Mouvements ;
- Affaires ;
- Préparations ;
- Inventaires ;
- Matériels ;
- Lots béton ;
- Emplacements ;
- Utilisateurs.

Une évolution d'un composant commun doit bénéficier à l'ensemble de
l'application.

## 2. Structure standard d'un module

Chaque module suit cette organisation :

```text
PageHeader
├── titre
├── description
└── actions principales

Barre de recherche et filtres

Liste ou tableau
└── sélection d'un objet

Fiche détaillée large
├── identité et statut
├── KPI
├── informations métier
├── lignes ou historique
└── ActionBar
```

## 3. Largeur des fiches détaillées

Le petit panneau historique de 480 px n'est plus adapté aux objets métier
complexes.

Trois formats sont disponibles :

| Format | Usage | Largeur PC |
|---|---|---:|
| `medium` | petite fiche simple | 55 % |
| `wide` | fiche métier standard | 68 % |
| `workspace` | préparation, inventaire, affaire complète | 82 % |

Le format par défaut est `wide`.

Sur tablette, les panneaux occupent environ 86 % de l'écran. Sur mobile, ils
occupent 100 % de la largeur.

## 4. Modèle Liste + Fiche

Pour les modules utilisés en continu, privilégier `SplitView` :

```tsx
<SplitView
  master={<Liste />}
  detail={<FicheDetaillee />}
/>
```

La liste reste visible sur grand écran et la fiche devient plein écran sur
tablette ou mobile.

Modules prioritaires :

1. Préparations ;
2. Inventaires ;
3. Affaires ;
4. Articles ;
5. Matériels ;
6. Lots béton ;
7. Emplacements.

## 5. Couleurs métier

Les couleurs ne sont jamais décoratives.

| Ton | Signification |
|---|---|
| `success` | disponible, terminé, conforme |
| `pending` | en attente, à préparer |
| `information` | information ou opération en cours |
| `validation` | décision ou validation requise |
| `warning` | écart, stock faible, retard |
| `danger` | rupture, refus, anomalie |
| `neutral` | archivé, inactif, information secondaire |

Le rouge COREF reste réservé à l'identité et aux actions principales.

## 6. Composants communs

### `PageHeader`

En-tête standard de chaque page.

### `Drawer`

Fiche détaillée superposée. Le format par défaut est désormais large.

```tsx
<Drawer
  open={selection !== null}
  title="PREP-000004"
  size="workspace"
  onClose={() => setSelection(null)}
>
  ...
</Drawer>
```

### `SplitView`

Disposition permanente Liste + Fiche.

### `StatusBadge`

Badge de statut avec une couleur métier.

### `KpiCard` et `KpiGrid`

Indicateurs synthétiques d'une fiche.

### `SectionCard`

Regroupe une section logique : informations, lignes, documents, historique.

### `ActionBar`

Regroupe les actions principales et secondaires. Peut rester visible en bas
d'une longue fiche avec `sticky`.

### `EmptyState`

Affichage homogène lorsqu'aucune donnée n'est présente.

## 7. Tableaux

Les tableaux métier doivent :

- conserver les libellés complets ;
- aligner les quantités à droite ;
- afficher l'unité ;
- différencier référence et désignation ;
- rendre la ligne entière cliquable ;
- conserver les actions importantes visibles ;
- rester utilisables au clavier ;
- prévoir un état vide clair.

Les tables très larges doivent être placées dans un conteneur avec défilement
horizontal, sans réduire les colonnes jusqu'à l'illisibilité.

## 8. Formulaires

- Libellé au-dessus du champ ;
- astérisque pour les champs obligatoires ;
- erreur directement sous le champ ou en tête du formulaire ;
- taille de clic minimale : 42 px ;
- aucune information métier importante uniquement indiquée par une couleur ;
- les listes doivent utiliser des utilisateurs ou référentiels réels, jamais
  une saisie libre lorsqu'une donnée structurée existe.

## 9. Actions

Ordre conseillé :

```text
Actions secondaires à gauche
Actions principales à droite
```

Exemple :

```text
Supprimer                          Enregistrer   Valider
```

Les actions destructives demandent une confirmation.

## 10. Accessibilité

- navigation complète au clavier ;
- focus visible ;
- boutons avec libellé ou `aria-label` ;
- contraste suffisant ;
- statuts exprimés par un texte, pas seulement une couleur ;
- panneau fermé avec un bouton clairement identifié ;
- mise en page mobile sans perte de fonctionnalité.

## 11. Impression

Les impressions doivent être indépendantes de l'interface écran :

- format A4 ;
- marges de 12 à 15 mm ;
- police lisible en noir et blanc ;
- titre et référence sur chaque page ;
- numéro de page ;
- date d'impression ;
- zones de signature ;
- QR code lorsque pertinent ;
- aucune barre de navigation imprimée.

## 12. Feuille de route de migration

### V2.0.1 — Préparations

- panneau `workspace` ;
- tableau des lignes ;
- ActionBar fixe ;
- ordre imprimable.

### V2.0.2 — Inventaires

- liste des campagnes ;
- fiche de comptage ;
- progression et anomalies.

### V2.0.3 — Affaires

- dossier chantier ;
- préparations, sorties, matériels et historique liés.

### V2.0.4 — Articles et stocks

- fiche article ;
- stocks, lots, réservations et mouvements.

### V2.0.5 — Matériels et emplacements

- fiches détaillées ;
- localisation et historique.
