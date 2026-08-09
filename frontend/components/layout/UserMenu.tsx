"use client";

import { LogOut } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import styles from "./UserMenu.module.css";

export function UserMenu() {
  const { utilisateur, deconnecter } = useAuth();

  const initiales =
    utilisateur.type_compte === "TECHNIQUE"
      ? "SE"
      : utilisateur.nom_complet
          .split(/\s+/)
          .slice(0, 2)
          .map((partie) => partie.charAt(0))
          .join("")
          .toUpperCase();

  return (
    <div className={styles.menu}>
      <div className={styles.avatar}>{initiales}</div>
      <div>
        <strong>{utilisateur.nom_complet}</strong>
        <span>
          {utilisateur.entreprise} ·{" "}
          {utilisateur.role.replaceAll("_", " ")}
        </span>
      </div>
      <button onClick={deconnecter} title="Se déconnecter">
        <LogOut size={17} />
      </button>
    </div>
  );
}
