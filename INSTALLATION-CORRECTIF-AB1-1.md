# Correctif Lot AB.1.1 — Script PowerShell

Le premier script AB.1 contenait une erreur d'échappement des guillemets dans
les commandes `python -c`.

Ce correctif ne touche à aucun fichier applicatif.

## Exécution

Extraire le ZIP à la racine de COREF Logistique puis lancer :

```powershell
powershell -ExecutionPolicy Bypass -File .\TESTER-LOT-AB1-1.ps1
```

Le script génère :

```text
AB1-PYTEST-COLLECT.txt
AB1-PYTEST-RESULTATS.txt
```

Envoyer ensuite la sortie PowerShell ou les deux fichiers.
