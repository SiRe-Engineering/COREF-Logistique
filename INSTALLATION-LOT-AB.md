# Installation / utilisation Lot AB

Ce lot est volontairement un **lot d'audit avant modification**.

Le Lot AA a démontré qu'un verrouillage global des API provoque des régressions tant
que tous les appels frontend ne transmettent pas le jeton.

## Étape 1

Extraire ce ZIP à la racine puis lancer :

```powershell
powershell -ExecutionPolicy Bypass -File .\AUDITER-LOT-AB.ps1
```

Envoyer la sortie complète.

Le script :
- affiche l'état Git ;
- recense les appels frontend à contrôler ;
- recense les routes backend déjà authentifiées ;
- lance la suite de tests dans le conteneur backend.

Il ne modifie ni le code ni la base.

## Étape 2

À partir de cette sortie, AB.1 corrigera les appels frontend réellement non
authentifiés puis protégera les routes backend correspondantes.

## Checkpoint Git

`PREPARER-CHECKPOINT-GIT-V1.ps1` affiche les commandes recommandées mais ne fait
aucun commit automatiquement.
