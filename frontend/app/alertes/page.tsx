"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BellRing,
  Check,
  CircleCheckBig,
  Clock3,
  RefreshCcw,
  Search,
  TriangleAlert,
} from "lucide-react";
import { entetesAuthentifiees } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";
import styles from "./page.module.css";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Alerte = {
  id: number;
  cle: string;
  categorie: string;
  niveau: string;
  titre: string;
  message: string;
  lien: string | null;
  source_type: string | null;
  source_id: number | null;
  statut: string;
  date_premiere_detection: string;
  date_derniere_detection: string;
  date_resolution: string | null;
  acquittee_par: string | null;
  date_acquittement: string | null;
};

type Resume = {
  actives: number;
  critiques: number;
  avertissements: number;
  acquittees: number;
};

export default function AlertesPage() {
  const [alertes, setAlertes] = useState<Alerte[]>([]);
  const [resume, setResume] = useState<Resume>({
    actives: 0,
    critiques: 0,
    avertissements: 0,
    acquittees: 0,
  });
  const [recherche, setRecherche] = useState("");
  const [statut, setStatut] = useState("OUVERTES");
  const [categorie, setCategorie] = useState("");
  const [chargement, setChargement] = useState(true);
  const [toast, setToast] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  async function charger() {
    setChargement(true);
    try {
      const [alertesResponse, resumeResponse] = await Promise.all([
        fetch(`${API_URL}/api/alertes`, {
          headers: entetesAuthentifiees(),
        }),
        fetch(`${API_URL}/api/alertes/resume`, {
          headers: entetesAuthentifiees(),
        }),
      ]);

      if (!alertesResponse.ok || !resumeResponse.ok) {
        throw new Error("Chargement impossible.");
      }

      setAlertes(await alertesResponse.json());
      setResume(await resumeResponse.json());
    } catch {
      setToast({
        type: "error",
        message: "Impossible de synchroniser les alertes.",
      });
    } finally {
      setChargement(false);
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const filtrees = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    return alertes.filter((alerte) => {
      const correspondRecherche =
        !terme ||
        alerte.titre.toLowerCase().includes(terme) ||
        alerte.message.toLowerCase().includes(terme);

      const correspondStatut =
        statut === "TOUTES"
          ? true
          : statut === "OUVERTES"
            ? ["ACTIVE", "ACQUITTEE"].includes(alerte.statut)
            : alerte.statut === statut;

      const correspondCategorie =
        !categorie || alerte.categorie === categorie;

      return (
        correspondRecherche &&
        correspondStatut &&
        correspondCategorie
      );
    });
  }, [alertes, recherche, statut, categorie]);

  async function changerStatut(
    alerte: Alerte,
    action: "acquitter" | "reactiver"
  ) {
    const response = await fetch(
      `${API_URL}/api/alertes/${alerte.id}/${action}`,
      {
        method: "PATCH",
        headers: entetesAuthentifiees(),
      }
    );
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      setToast({
        type: "error",
        message:
          typeof data?.detail === "string"
            ? data.detail
            : "Action impossible.",
      });
      return;
    }

    await charger();
    setToast({
      type: "success",
      message:
        action === "acquitter"
          ? "Alerte acquittée."
          : "Alerte réactivée.",
    });
  }

  return (
    <div>
      <div className="breadcrumb">Pilotage / Alertes</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Centre de vigilance</span>
          <h1>Alertes logistiques</h1>
          <p>
            Les alertes disparaissent automatiquement lorsque leur cause
            métier est réellement corrigée.
          </p>
        </div>

        <Button variant="secondary" onClick={charger}>
          <RefreshCcw size={17} />
          Synchroniser
        </Button>
      </div>

      <section className={styles.metrics}>
        <Metric
          icon={<BellRing size={21} />}
          label="Ouvertes"
          value={resume.actives}
        />
        <Metric
          icon={<AlertTriangle size={21} />}
          label="Critiques"
          value={resume.critiques}
          critical
        />
        <Metric
          icon={<TriangleAlert size={21} />}
          label="Avertissements"
          value={resume.avertissements}
          warning
        />
        <Metric
          icon={<Check size={21} />}
          label="Acquittées"
          value={resume.acquittees}
        />
      </section>

      <section className={styles.toolbar}>
        <label className="search-field">
          <Search size={17} />
          <input
            type="search"
            value={recherche}
            placeholder="Rechercher une alerte"
            onChange={(event) => setRecherche(event.target.value)}
          />
        </label>

        <select
          value={statut}
          onChange={(event) => setStatut(event.target.value)}
        >
          <option value="OUVERTES">Alertes ouvertes</option>
          <option value="ACTIVE">Actives uniquement</option>
          <option value="ACQUITTEE">Acquittées</option>
          <option value="RESOLUE">Résolues</option>
          <option value="TOUTES">Toutes</option>
        </select>

        <select
          value={categorie}
          onChange={(event) => setCategorie(event.target.value)}
        >
          <option value="">Toutes les catégories</option>
          <option value="STOCK">Stock</option>
          <option value="PEREMPTION">Péremption</option>
          <option value="PREPARATION">Préparation</option>
          <option value="INVENTAIRE">Inventaire</option>
        </select>
      </section>

      <section className={styles.list}>
        {filtrees.map((alerte) => (
          <article
            key={alerte.id}
            className={`${styles.alert} ${
              alerte.niveau === "CRITIQUE"
                ? styles.critical
                : styles.warning
            } ${
              alerte.statut === "ACQUITTEE"
                ? styles.acknowledged
                : alerte.statut === "RESOLUE"
                  ? styles.resolved
                  : ""
            }`}
          >
            <div className={styles.icon}>
              {alerte.statut === "RESOLUE" ? (
                <CircleCheckBig size={22} />
              ) : alerte.niveau === "CRITIQUE" ? (
                <AlertTriangle size={22} />
              ) : (
                <TriangleAlert size={22} />
              )}
            </div>

            <div className={styles.content}>
              <div className={styles.titleLine}>
                <strong>{alerte.titre}</strong>
                <span>{alerte.categorie}</span>
                <span>{alerte.statut}</span>
              </div>

              <p>{alerte.message}</p>

              <small>
                <Clock3 size={13} />
                Détectée le{" "}
                {new Intl.DateTimeFormat("fr-FR", {
                  dateStyle: "short",
                  timeStyle: "short",
                }).format(new Date(alerte.date_premiere_detection))}
                {alerte.acquittee_par
                  ? ` · acquittée par ${alerte.acquittee_par}`
                  : ""}
              </small>
            </div>

            <div className={styles.actions}>
              {alerte.lien && alerte.statut !== "RESOLUE" && (
                <Link href={alerte.lien}>Ouvrir</Link>
              )}

              {alerte.statut === "ACTIVE" && (
                <button
                  onClick={() =>
                    changerStatut(alerte, "acquitter")
                  }
                >
                  <Check size={15} />
                  Acquitter
                </button>
              )}

              {alerte.statut === "ACQUITTEE" && (
                <button
                  onClick={() =>
                    changerStatut(alerte, "reactiver")
                  }
                >
                  <RefreshCcw size={15} />
                  Réactiver
                </button>
              )}
            </div>
          </article>
        ))}

        {!chargement && filtrees.length === 0 && (
          <div className={styles.empty}>
            <CircleCheckBig size={42} />
            <strong>Aucune alerte</strong>
            <span>
              Aucun signal ne correspond aux filtres sélectionnés.
            </span>
          </div>
        )}

        {chargement && (
          <div className={styles.empty}>
            Synchronisation des alertes…
          </div>
        )}
      </section>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
  critical = false,
  warning = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  critical?: boolean;
  warning?: boolean;
}) {
  return (
    <article
      className={`${styles.metric} ${
        critical
          ? styles.metricCritical
          : warning
            ? styles.metricWarning
            : ""
      }`}
    >
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
