# Correctif AB.1.3 — tests Stock obsolètes

## Cause

`StockSet` ne gère plus `quantite_reservee`.

L'architecture actuelle sépare :

```text
StockSet
→ quantité physique

ReservationStock
→ réservations métier
```

Le test historique vérifiait encore l'ancienne architecture et attendait :

```text
quantite_reservee
```

dans `StockSet`.

Un test plus récent du projet confirme déjà explicitement que ce champ ne doit
plus être présent dans `StockSet`.

## Correction

Le test vérifie désormais :

- la création d'un stock physique valide ;
- l'absence volontaire de `quantite_reservee` dans `StockSet` ;
- le refus d'une quantité physique négative.

Aucun code métier n'est modifié.

## Exécution

Après extraction à la racine :

```powershell
powershell -ExecutionPolicy Bypass -File .\APPLIQUER-ET-TESTER-AB1-3.ps1
```

Le script lance les tests Stock ciblés puis toute la suite Pytest.

Résultat espéré :

```text
113 passed
```
