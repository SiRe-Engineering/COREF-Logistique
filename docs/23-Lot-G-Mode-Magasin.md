# Lot G — Mode magasin

Le mode magasin est une couche opérateur au-dessus des modules existants.

## Principe scanner

Le lecteur n’a besoin d’aucun pilote applicatif spécifique. Un lecteur HID
USB ou Bluetooth configuré comme clavier saisit le code dans le champ actif et
termine par `Enter`.

## Identifiants V1

Les identifiants déjà présents dans COREF Logistique deviennent les valeurs
scannables :

```text
ART-000001
LOT-000001
numéro de lot fournisseur
```

Cela évite d’introduire prématurément un second référentiel de codes.

## Évolutions prévues

Les actions de préparation, retour et inventaire restent volontairement dans
leurs modules métier pour ce lot. Une V2 pourra ouvrir directement une ligne
de préparation ou d’inventaire à partir d’un scan.
