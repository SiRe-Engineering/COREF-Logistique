"use client";

import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  enregistrerJeton,
  entetesAuthentifiees,
  lireJeton,
  supprimerJeton,
  Utilisateur,
} from "@/lib/auth";
import styles from "./AuthProvider.module.css";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type AuthContextValue = {
  utilisateur: Utilisateur | null;
  chargerUtilisateur: () => Promise<void>;
  deconnecter: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);


type ApiErrorDetail =
  | string
  | Array<{
      msg?: string;
      loc?: Array<string | number>;
    }>
  | null
  | undefined;

function messageErreur(detail: ApiErrorDetail) {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((erreur) => {
        const champ = Array.isArray(erreur.loc)
          ? erreur.loc
              .filter((element) => element !== "body")
              .join(" > ")
          : "";

        if (champ && erreur.msg) {
          return `${champ} : ${erreur.msg}`;
        }

        return erreur.msg ?? null;
      })
      .filter((message): message is string => Boolean(message));

    if (messages.length > 0) {
      return messages.join(" · ");
    }
  }

  return "Connexion impossible.";
}


export function useAuth() {
  const contexte = useContext(AuthContext);
  if (!contexte) {
    throw new Error("useAuth doit être utilisé dans AuthProvider.");
  }
  return contexte;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [utilisateur, setUtilisateur] = useState<Utilisateur | null>(null);
  const [chargement, setChargement] = useState(true);
  const [email, setEmail] = useState("admin@coref.fr");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState("");

  async function chargerUtilisateur() {
    const jeton = lireJeton();
    if (!jeton) {
      setUtilisateur(null);
      setChargement(false);
      return;
    }

    const response = await fetch(`${API_URL}/api/auth/me`, {
      headers: entetesAuthentifiees(),
    });

    if (!response.ok) {
      supprimerJeton();
      setUtilisateur(null);
      setChargement(false);
      return;
    }

    setUtilisateur(await response.json());
    setChargement(false);
  }

  useEffect(() => {
    chargerUtilisateur();
  }, []);

  async function connecter(event: React.FormEvent) {
    event.preventDefault();
    setErreur("");

    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        mot_de_passe: motDePasse,
      }),
    });

    if (!response.ok) {
      const detail = await response.json().catch(() => null);
      setErreur(messageErreur(detail?.detail));
      return;
    }

    const data = await response.json();
    enregistrerJeton(data.jeton);
    setUtilisateur(data.utilisateur);
    setMotDePasse("");
  }

  async function deconnecter() {
    await fetch(`${API_URL}/api/auth/logout`, {
      method: "POST",
      headers: entetesAuthentifiees(),
    }).catch(() => null);

    supprimerJeton();
    setUtilisateur(null);
  }

  if (chargement) {
    return <div className={styles.loading}>Chargement de la session…</div>;
  }

  if (!utilisateur) {
    return (
      <main className={styles.loginPage}>
        <section className={styles.loginCard}>
          <div className={styles.logo}>CL</div>
          <div>
            <span>COREF Logistique</span>
            <h1>Connexion</h1>
            <p>Identifiez-vous pour accéder à l’application.</p>
          </div>

          <form onSubmit={connecter}>
            <label>
              <span>Adresse e-mail</span>
              <input
                required
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>

            <label>
              <span>Mot de passe</span>
              <input
                required
                type="password"
                value={motDePasse}
                onChange={(event) =>
                  setMotDePasse(event.target.value)
                }
              />
            </label>

            {erreur && <div className={styles.error}>{erreur}</div>}

            <button type="submit">Se connecter</button>
          </form>

          <small>
            Compte initial : admin@coref.fr
          </small>
        </section>
      </main>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        utilisateur,
        chargerUtilisateur,
        deconnecter,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
