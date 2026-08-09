# Modèle de données — COREF Logistique

## Article

Un article est rattaché à une famille et, facultativement, à une sous-famille.

La référence interne est générée automatiquement par PostgreSQL selon le format :

```text
ART-000001
```

Une référence manuelle peut être fournie uniquement pour les reprises de données
ou les cas exceptionnels.

## Relations

```text
FAMILLE 1 ─── N SOUS_FAMILLE
FAMILLE 1 ─── N ARTICLE
SOUS_FAMILLE 1 ─── N ARTICLE
```

Une sous-famille sélectionnée doit obligatoirement appartenir à la famille de
l’article.
