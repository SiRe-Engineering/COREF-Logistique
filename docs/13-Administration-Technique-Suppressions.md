# Administration technique — suppressions auditables

## Principe

Les données de traçabilité ne sont jamais effacées physiquement.

- un lot supprimé est archivé ;
- une écriture supprimée est annulée et contre-passée.

Cette approche conserve les preuves nécessaires à la compréhension des stocks
et permet d’identifier l’administrateur technique ayant réalisé l’opération.

## Rôle autorisé

```text
ADMINISTRATEUR_TECHNIQUE
```

## Endpoints

```text
DELETE /api/lots-beton/{lot_id}
DELETE /api/mouvements/{mouvement_id}
```

Les deux endpoints exigent un corps JSON :

```json
{
  "motif": "Description obligatoire de la correction"
}
```
