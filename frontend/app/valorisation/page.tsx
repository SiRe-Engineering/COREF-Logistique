"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ChartNoAxesCombined,
  CircleDollarSign,
  Layers3,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { entetesAuthentifiees } from "@/lib/auth";
import { Toast } from "@/components/ui/Toast";
import styles from "./page.module.css";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Historique = {
  mois: string;
  valeur_physique: string;
  valeur_reservee: string;
  valeur_disponible: string;
  date_mise_a_jour: string;
};

type Famille = {
  famille_id: number | null;
  famille: string;
  valeur_physique: string;
  valeur_reservee: string;
  valeur_disponible: string;
  part_physique_pct: string;
};

type Valorisation = {
  resume: {
    valeur_physique: string;
    valeur_reservee: string;
    valeur_disponible: string;
    variation_mensuelle_pct: string | null;
  };
  historique: Historique[];
  familles: Famille[];
};

function euro(value: string | number) {
  return Number(value).toLocaleString("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  });
}

function moisCourt(value: string) {
  return new Intl.DateTimeFormat("fr-FR", {
    month: "short",
    year: "2-digit",
  }).format(new Date(`${value}T12:00:00`));
}

export default function ValorisationPage() {
  const [data, setData] = useState<Valorisation | null>(null);
  const [periode, setPeriode] = useState<6 | 12 | 24>(12);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const response = await fetch(`${API_URL}/api/valorisation`, {
        headers: entetesAuthentifiees(),
      });
      const json = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(
          typeof json?.detail === "string"
            ? json.detail
            : "Chargement impossible."
        );
      }
      setData(json);
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Chargement impossible.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const historique = useMemo(
    () => data?.historique.slice(-periode) ?? [],
    [data, periode]
  );

  const variation = data?.resume.variation_mensuelle_pct;
  const variationNombre =
    variation === null || variation === undefined
      ? null
      : Number(variation);

  return (
    <div>
      <div className="breadcrumb">
        Pilotage / Valorisation
      </div>

      <div className="page-heading">
        <span className="eyebrow">Analyse financière des stocks</span>
        <h1>Valorisation</h1>
        <p>
          Suivez la valeur globale du stock et sa répartition par famille.
        </p>
      </div>

      {data && (
        <>
          <section className={styles.kpis}>
            <Kpi
              icon={<CircleDollarSign size={23} />}
              label="Valeur physique"
              value={euro(data.resume.valeur_physique)}
            />
            <Kpi
              icon={<Layers3 size={23} />}
              label="Valeur réservée"
              value={euro(data.resume.valeur_reservee)}
            />
            <Kpi
              icon={<ChartNoAxesCombined size={23} />}
              label="Valeur disponible"
              value={euro(data.resume.valeur_disponible)}
            />
            <Kpi
              icon={
                variationNombre !== null && variationNombre < 0
                  ? <TrendingDown size={23} />
                  : <TrendingUp size={23} />
              }
              label="Variation mensuelle"
              value={
                variationNombre === null
                  ? "—"
                  : `${variationNombre > 0 ? "+" : ""}${variationNombre.toLocaleString(
                      "fr-FR",
                      { maximumFractionDigits: 1 }
                    )} %`
              }
            />
          </section>

          <section className={styles.panel}>
            <div className={styles.panelHeader}>
              <div>
                <span className="eyebrow">Historique</span>
                <h2>Évolution mensuelle de la valeur globale</h2>
              </div>
              <div className={styles.periods}>
                {[6, 12, 24].map((value) => (
                  <button
                    key={value}
                    className={
                      periode === value ? styles.periodActive : ""
                    }
                    onClick={() =>
                      setPeriode(value as 6 | 12 | 24)
                    }
                  >
                    {value} mois
                  </button>
                ))}
              </div>
            </div>

            <EvolutionChart historique={historique} />

            {historique.length < 2 && (
              <p className={styles.historyNote}>
                L’historique démarre avec le Lot I-B. Le snapshot du mois
                courant sera mis à jour automatiquement à chaque mouvement de
                stock et chaque modification du CUMP.
              </p>
            )}
          </section>

          <section className={styles.familyGrid}>
            <div className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <span className="eyebrow">Structure du stock</span>
                  <h2>Répartition par famille</h2>
                </div>
              </div>

              <div className={styles.familyBars}>
                {data.familles.map((famille) => (
                  <article key={famille.famille_id ?? "none"}>
                    <div className={styles.familyBarHeader}>
                      <strong>{famille.famille}</strong>
                      <span>
                        {euro(famille.valeur_physique)}
                        {" · "}
                        {Number(famille.part_physique_pct).toLocaleString(
                          "fr-FR",
                          { maximumFractionDigits: 1 }
                        )}
                        %
                      </span>
                    </div>
                    <div className={styles.barTrack}>
                      <div
                        className={styles.barFill}
                        style={{
                          width: `${Math.min(
                            Number(famille.part_physique_pct),
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </article>
                ))}
              </div>
            </div>

            <div className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <span className="eyebrow">Détail</span>
                  <h2>Valeur par famille</h2>
                </div>
              </div>

              <div className={styles.tableWrap}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>Famille</th>
                      <th>Physique</th>
                      <th>Réservée</th>
                      <th>Disponible</th>
                      <th>%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.familles.map((famille) => (
                      <tr key={famille.famille_id ?? "none"}>
                        <td><strong>{famille.famille}</strong></td>
                        <td>{euro(famille.valeur_physique)}</td>
                        <td>{euro(famille.valeur_reservee)}</td>
                        <td>{euro(famille.valeur_disponible)}</td>
                        <td>
                          {Number(famille.part_physique_pct).toLocaleString(
                            "fr-FR",
                            { maximumFractionDigits: 1 }
                          )}
                          %
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        </>
      )}

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

function Kpi({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <article className={styles.kpi}>
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function EvolutionChart({
  historique,
}: {
  historique: Historique[];
}) {
  const width = 1000;
  const height = 310;
  const paddingX = 55;
  const paddingY = 34;

  if (historique.length === 0) {
    return (
      <div className={styles.emptyChart}>
        Aucun historique disponible.
      </div>
    );
  }

  const values = historique.flatMap((item) => [
    Number(item.valeur_physique),
    Number(item.valeur_reservee),
    Number(item.valeur_disponible),
  ]);
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const amplitude = Math.max(max - min, 1);

  function x(index: number) {
    if (historique.length === 1) return width / 2;
    return (
      paddingX +
      (index * (width - paddingX * 2)) /
        (historique.length - 1)
    );
  }

  function y(value: number) {
    return (
      height -
      paddingY -
      ((value - min) / amplitude) * (height - paddingY * 2)
    );
  }

  function points(key: keyof Pick<
    Historique,
    "valeur_physique" | "valeur_reservee" | "valeur_disponible"
  >) {
    return historique
      .map((item, index) => `${x(index)},${y(Number(item[key]))}`)
      .join(" ");
  }

  return (
    <div className={styles.chartWrap}>
      <div className={styles.legend}>
        <span><i className={styles.legendPhysical} />Physique</span>
        <span><i className={styles.legendReserved} />Réservée</span>
        <span><i className={styles.legendAvailable} />Disponible</span>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className={styles.chart}
        role="img"
        aria-label="Évolution mensuelle de la valeur du stock"
      >
        {[0, 1, 2, 3, 4].map((step) => {
          const yy =
            paddingY +
            (step * (height - paddingY * 2)) / 4;
          const value =
            max - (step * amplitude) / 4;
          return (
            <g key={step}>
              <line
                x1={paddingX}
                x2={width - paddingX}
                y1={yy}
                y2={yy}
                className={styles.gridLine}
              />
              <text
                x={paddingX - 8}
                y={yy + 4}
                textAnchor="end"
                className={styles.axisText}
              >
                {Math.round(value / 1000)}k€
              </text>
            </g>
          );
        })}

        <polyline
          points={points("valeur_physique")}
          className={`${styles.line} ${styles.linePhysical}`}
        />
        <polyline
          points={points("valeur_reservee")}
          className={`${styles.line} ${styles.lineReserved}`}
        />
        <polyline
          points={points("valeur_disponible")}
          className={`${styles.line} ${styles.lineAvailable}`}
        />

        {historique.map((item, index) => (
          <text
            key={item.mois}
            x={x(index)}
            y={height - 8}
            textAnchor="middle"
            className={styles.axisText}
          >
            {moisCourt(item.mois)}
          </text>
        ))}
      </svg>
    </div>
  );
}
