"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { Printer } from "lucide-react";
import { Button } from "@/components/ui";
import styles from "./page.module.css";

type Article = {
  reference: string;
  designation: string;
  unite: string;
};

type Lot = {
  numero_lot_fournisseur: string;
};

type Emplacement = {
  code: string;
  nom: string;
};

type Ligne = {
  id: number;
  statut: string;
  quantite_demandee: string;
  quantite_preparee: string;
  quantite_manquante: string;
  commentaire: string | null;
  motif_ecart: string | null;
  article: Article;
  lot: Lot | null;
  emplacement_source: Emplacement | null;
};

type Preparation = {
  id: number;
  reference: string;
  nom: string;
  statut: string;
  date_besoin: string | null;
  demandeur: string | null;
  preparateur: string | null;
  vehicule: string | null;
  commentaire: string | null;
  date_creation: string;
  affaire: {
    reference: string;
    code_externe: string | null;
    nom: string;
    client: string | null;
    site: string | null;
    zone_intervention: string | null;
    charge_affaires: string | null;
    date_debut: string | null;
    date_fin_prevue: string | null;
  };
  lignes: Ligne[];
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function formaterDate(value: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("fr-FR").format(new Date(value));
}

function libelleStatutLigne(statut: string) {
  const libelles: Record<string, string> = {
    A_PREPARER: "À préparer",
    PREPAREE: "Préparée",
    PARTIELLE: "Partielle",
    INDISPONIBLE: "Indisponible",
    EXPEDIEE: "Expédiée",
  };

  return libelles[statut] ?? statut.replaceAll("_", " ");
}

function classeStatut(statut: string) {
  if (statut === "PREPAREE" || statut === "EXPEDIEE") {
    return styles.success;
  }
  if (statut === "PARTIELLE") {
    return styles.warning;
  }
  if (statut === "INDISPONIBLE") {
    return styles.danger;
  }
  return styles.neutral;
}

export default function ImpressionPreparationPage() {
  const params = useParams<{ id: string }>();
  const [preparation, setPreparation] = useState<Preparation | null>(null);
  const [erreur, setErreur] = useState("");

  useEffect(() => {
    async function charger() {
      try {
        const response = await fetch(
          `${API_URL}/api/preparations/${params.id}`
        );
        const data = await response.json().catch(() => null);

        if (!response.ok) {
          throw new Error(
            typeof data?.detail === "string"
              ? data.detail
              : "Chargement impossible."
          );
        }

        setPreparation(data);
      } catch (error) {
        setErreur(
          error instanceof Error
            ? error.message
            : "Chargement impossible."
        );
      }
    }

    charger();
  }, [params.id]);

  const indicateurs = useMemo(() => {
    if (!preparation) {
      return {
        references: 0,
        completes: 0,
        partielles: 0,
        indisponibles: 0,
      };
    }

    return {
      references: preparation.lignes.length,
      completes: preparation.lignes.filter(
        (ligne) => ligne.statut === "PREPAREE"
      ).length,
      partielles: preparation.lignes.filter(
        (ligne) => ligne.statut === "PARTIELLE"
      ).length,
      indisponibles: preparation.lignes.filter(
        (ligne) => ligne.statut === "INDISPONIBLE"
      ).length,
    };
  }, [preparation]);

  if (erreur) {
    return <main className={styles.message}>{erreur}</main>;
  }

  if (!preparation) {
    return <main className={styles.message}>Chargement…</main>;
  }

  return (
    <main className={styles.page}>
      <div className={styles.screenActions}>
        <Button onClick={() => window.print()}>
          <Printer size={17} />
          Imprimer / Enregistrer en PDF
        </Button>
      </div>

      <header className={styles.header}>
        <div className={styles.brand}>
          <strong>COREF</strong>
          <span>LOGISTIQUE</span>
        </div>

        <div className={styles.documentTitle}>
          <span>ORDRE DE PRÉPARATION</span>
          <h1>{preparation.reference}</h1>
          <p>{preparation.nom}</p>
        </div>

        <div className={styles.printMeta}>
          <span>Imprimé le</span>
          <strong>
            {new Intl.DateTimeFormat("fr-FR", {
              dateStyle: "short",
              timeStyle: "short",
            }).format(new Date())}
          </strong>
          <span>Statut</span>
          <strong>{preparation.statut.replaceAll("_", " ")}</strong>
        </div>
      </header>

      <section className={styles.identity}>
        <div>
          <span>Affaire</span>
          <strong>
            {preparation.affaire.code_externe ||
              preparation.affaire.reference}
          </strong>
          <small>{preparation.affaire.nom}</small>
        </div>
        <div>
          <span>Client</span>
          <strong>{preparation.affaire.client ?? "—"}</strong>
        </div>
        <div>
          <span>Site / Zone</span>
          <strong>{preparation.affaire.site ?? "—"}</strong>
          <small>
            {preparation.affaire.zone_intervention ?? "—"}
          </small>
        </div>
        <div>
          <span>Demandeur</span>
          <strong>{preparation.demandeur ?? "—"}</strong>
        </div>
        <div>
          <span>Préparateur</span>
          <strong>{preparation.preparateur ?? "—"}</strong>
        </div>
        <div>
          <span>Besoin / Fin prévue</span>
          <strong>{formaterDate(preparation.date_besoin)}</strong>
          <small>
            {formaterDate(preparation.affaire.date_fin_prevue)}
          </small>
        </div>
      </section>

      <section className={styles.summary}>
        <div>
          <span>Références</span>
          <strong>{indicateurs.references}</strong>
        </div>
        <div>
          <span>Complètes</span>
          <strong>{indicateurs.completes}</strong>
        </div>
        <div>
          <span>Partielles</span>
          <strong>{indicateurs.partielles}</strong>
        </div>
        <div>
          <span>Indisponibles</span>
          <strong>{indicateurs.indisponibles}</strong>
        </div>
        <div>
          <span>Véhicule</span>
          <strong>{preparation.vehicule ?? "—"}</strong>
        </div>
      </section>

      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.checkbox}>✓</th>
            <th>Statut</th>
            <th>Article</th>
            <th>Lot</th>
            <th>Emplacement</th>
            <th>Demandé</th>
            <th>Préparé</th>
            <th>Manquant</th>
            <th>Observations</th>
          </tr>
        </thead>
        <tbody>
          {preparation.lignes.map((ligne) => (
            <tr key={ligne.id}>
              <td className={styles.checkbox}>□</td>
              <td>
                <span
                  className={`${styles.status} ${classeStatut(
                    ligne.statut
                  )}`}
                >
                  {libelleStatutLigne(ligne.statut)}
                </span>
              </td>
              <td>
                <strong>{ligne.article.reference}</strong>
                <small>{ligne.article.designation}</small>
              </td>
              <td>{ligne.lot?.numero_lot_fournisseur ?? "—"}</td>
              <td>
                <strong>{ligne.emplacement_source?.code ?? "—"}</strong>
                <small>{ligne.emplacement_source?.nom ?? ""}</small>
              </td>
              <td className={styles.number}>
                {Number(ligne.quantite_demandee).toLocaleString(
                  "fr-FR"
                )}{" "}
                {ligne.article.unite}
              </td>
              <td className={styles.number}>
                {Number(ligne.quantite_preparee).toLocaleString(
                  "fr-FR"
                )}{" "}
                {ligne.article.unite}
              </td>
              <td className={styles.number}>
                {Number(ligne.quantite_manquante).toLocaleString(
                  "fr-FR"
                )}{" "}
                {ligne.article.unite}
              </td>
              <td>
                {ligne.motif_ecart || ligne.commentaire || "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <section className={styles.notes}>
        <h2>Remarques générales</h2>
        <p>{preparation.commentaire ?? ""}</p>
        <div />
        <div />
      </section>

      <footer className={styles.validation}>
        <div>
          <span>Préparation terminée</span>
          <strong>□ Oui &nbsp;&nbsp; □ Non</strong>
        </div>
        <div>
          <span>Date</span>
          <strong>________________</strong>
        </div>
        <div>
          <span>Heure</span>
          <strong>________________</strong>
        </div>
        <div className={styles.signature}>
          <span>Signature du préparateur</span>
          <strong />
        </div>
      </footer>
    </main>
  );
}
