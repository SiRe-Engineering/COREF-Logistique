# Correctif frontend du lot 18.3A

Remplacer :

```text
frontend/app/preparations/page.tsx
```

Puis reconstruire le frontend :

```powershell
docker compose up --build -d frontend
docker compose logs frontend --tail=100
```

Le correctif ajoute les fonctions manquantes :

- `proposerRemplacement`
- `deciderRemplacement`

Il ajoute également l'import :

```tsx
import { entetesAuthentifiees } from "@/lib/auth";
```
