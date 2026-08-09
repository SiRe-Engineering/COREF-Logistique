# Correctif AB.1.2 — test de remplacement obsolète

L'ancien test importait `RemplacementPreparation`, modèle qui n'existe plus dans
l'architecture actuelle.

Le remplacement est désormais porté directement par `LignePreparation` via :

- `article_remplacement_id`
- `lot_remplacement_id`
- `emplacement_remplacement_id`
- `quantite_remplacement`
- `commentaire_remplacement`
- `propose_par`
- `decision_remplacement`
- `decision_par`
- `commentaire_decision`
- les statuts `REMPLACEMENT_PROPOSE`, `REMPLACEMENT_ACCEPTE`, `REMPLACEMENT_REFUSE`

AB.1.2 remplace uniquement le test obsolète. Aucun modèle, aucune API et aucune
migration ne sont modifiés.

## Installation

Extraire à la racine puis :

```powershell
powershell -ExecutionPolicy Bypass -File .\APPLIQUER-ET-TESTER-AB1-2.ps1
```

Le script teste d'abord le fichier corrigé puis lance toute la suite Pytest et
écrit `AB1-2-PYTEST-RESULTATS.txt`.
