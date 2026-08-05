export type Utilisateur = {
  id: number;
  nom_complet: string;
  prenom: string | null;
  nom: string | null;
  email: string;
  role: string;
  type_compte: string;
  entreprise: string;
  fonction: string | null;
  actif: boolean;
};

const TOKEN_KEY = "coref-auth-token";

export function lireJeton() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function enregistrerJeton(jeton: string) {
  localStorage.setItem(TOKEN_KEY, jeton);
}

export function supprimerJeton() {
  localStorage.removeItem(TOKEN_KEY);
}

export function entetesAuthentifiees(
  complement?: HeadersInit
): HeadersInit {
  const jeton = lireJeton();

  return {
    ...(complement ?? {}),
    ...(jeton ? { Authorization: `Bearer ${jeton}` } : {}),
  };
}
