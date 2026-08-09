# Lot Z — Dashboard Logistique V2

## Objectif

La page d'accueil devient le cockpit opérationnel de COREF Logistique.

Elle consolide les modules déjà validés sans créer de nouvelles données :

- valeur du stock ;
- ruptures et niveaux mini ;
- centre d'alertes ;
- préparations ;
- achats et livraisons fournisseurs ;
- OTD ;
- maintenance et contrôles matériel ;
- lots béton ;
- inventaires ;
- notifications utilisateur.

## Principe technique

Aucune migration et aucun nouveau modèle backend.

Le dashboard consomme les API déjà existantes :

```text
/api/dashboard
/api/alertes-logistiques
/api/achats/pilotage
/api/maintenance-materiel/dashboard
/api/notifications/me
```

Si un sous-module est momentanément indisponible, le reste du tableau de bord
continue de s'afficher.

## Installation

Remplacer :

```text
frontend/app/page.tsx
frontend/app/page.module.css
```

Puis :

```powershell
docker compose up --build -d frontend
docker compose logs frontend --tail=120
```

Puis `Ctrl + F5`.

## Recette

1. Vérifier la valeur globale du stock.
2. Vérifier que les alertes critiques sont identiques au Centre d'alertes.
3. Vérifier les préparations à traiter / en retard.
4. Vérifier les commandes ouvertes / en retard.
5. Vérifier les livraisons attendues.
6. Vérifier les contrôles matériel.
7. Vérifier les lots béton à échéance.
8. Cliquer chaque bloc et confirmer qu'il ouvre le bon module.
9. Vérifier les notifications et le bouton de lecture.
