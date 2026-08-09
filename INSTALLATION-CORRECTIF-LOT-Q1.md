# Correctif Lot Q.1 — FDS obligatoire & désignation article

## Modifications

1. La carte de conformité d'un lot béton affiche maintenant :
   - référence du lot ;
   - désignation de l'article ;
   - référence article ;
   - statut documentaire.

2. Seule la FDS est obligatoire.

Le certificat fournisseur reste disponible dans le module documentaire mais
devient facultatif.

## Règles

- aucune FDS : `INCOMPLET`
- FDS présente et valide : `COMPLET`
- FDS présente mais expirée : `EXPIRE`

L'absence ou l'expiration d'un certificat ne modifie pas le statut de
conformité du lot.

## Installation

Remplacer les fichiers du correctif puis :

```powershell
docker compose up --build -d backend frontend
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
```

Aucune migration Alembic supplémentaire.

Puis `Ctrl + F5`.

## Recette

Sur un lot béton :
1. sans FDS → INCOMPLET ;
2. déposer uniquement une FDS → COMPLET ;
3. vérifier que la désignation et la référence article apparaissent ;
4. supprimer la FDS → INCOMPLET ;
5. déposer une FDS avec date d'expiration passée → EXPIRE.
