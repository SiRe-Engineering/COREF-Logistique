# COREF Logistique V2.0.0 — Fondation UX

## Contenu

- nouveau panneau détaillé grand format ;
- largeur par défaut de 68 % de l'écran ;
- mode `workspace` à 82 % pour les opérations complexes ;
- plein écran sur téléphone ;
- composants communs :
  - PageHeader ;
  - StatusBadge ;
  - KpiCard ;
  - KpiGrid ;
  - SectionCard ;
  - ActionBar ;
  - SplitView ;
  - EmptyState ;
- documentation `docs/Design-System.md`.

## Installation

Copier tous les fichiers du lot à la racine du dépôt en acceptant les
remplacements.

Puis :

```powershell
docker compose restart frontend
```

Si Next.js ne recharge pas les nouveaux modules CSS :

```powershell
docker compose up --build -d frontend
```

Aucune migration de base de données n'est nécessaire.

## Effet immédiat

Toutes les pages utilisant déjà le composant `Drawer` bénéficient
automatiquement d'un panneau beaucoup plus large.

Largeur par défaut :

```text
68 % de la largeur de l'écran
minimum 820 px
maximum 1 380 px
```

Sur les écrans intermédiaires : environ 86 %.

Sur mobile : 100 %.

## Utilisation spécifique

Pour une préparation ou un inventaire complexe :

```tsx
<Drawer
  open={selection !== null}
  title={selection?.reference ?? ""}
  size="workspace"
  onClose={() => setSelection(null)}
>
  ...
</Drawer>
```

Pour une petite fiche :

```tsx
<Drawer
  open={selection !== null}
  title="Détail"
  size="medium"
  onClose={fermer}
>
  ...
</Drawer>
```

## Vérifications

Tester successivement :

- Préparations ;
- Stocks ;
- Inventaires ;
- Affaires ;
- Articles ;
- Matériels ;
- Emplacements.

Le panneau doit prendre au moins la moitié de l'écran et rester utilisable
sans écraser les tableaux ou formulaires.

## Git

```powershell
git status
git add frontend/components/ui docs/Design-System.md INSTALLATION-V2-0-0.md
git commit -m "feat: add V2 UX foundation and wide detail panels"
git push
```
