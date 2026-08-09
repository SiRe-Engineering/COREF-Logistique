"use client";

import { apiFetch } from "@/lib/api";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Bell,
  Boxes,
  Check,
  ChevronRight,
  CircleAlert,
  ClipboardCheck,
  Clock3,
  Euro,
  PackageCheck,
  PackageX,
  RefreshCcw,
  ShieldCheck,
  ShoppingCart,
  TriangleAlert,
  Truck,
  Wrench,
} from "lucide-react";

import { useAuth } from "@/components/auth/AuthProvider";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";
import { entetesAuthentifiees } from "@/lib/auth";
import styles from "./page.module.css";

const API =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Notification = {
  id: number;
  titre: string;
  message: string;
  lien: string | null;
  lue: boolean;
  date_creation: string;
};

type Dashboard = {
  kpis: {
    articles_actifs: number;
    ruptures: number;
    stocks_sous_seuil: number;
    lots_a_perimer: number;
    preparations_a_traiter: number;
    preparations_en_retard: number;
    inventaires_en_cours: number;
    retours_en_attente: number;
    valeur_stock_physique: string;
    valeur_stock_reservee: string;
    valeur_stock_disponible: string;
    valeur_lots_a_perimer: string;
  };
  stocks: any[];
  lots: any[];
  preparations: any[];
  inventaires: any[];
};

type Alertes = {
  total: number;
  critiques: number;
  attention: number;
  info: number;
  alertes: Array<{
    key: string;
    niveau: "CRITIQUE" | "ATTENTION" | "INFO";
    categorie: string;
    titre: string;
    detail: string;
    href: string;
    echeance?: string | null;
  }>;
};

type Achats = {
  kpis: {
    commandes_ouvertes: number;
    commandes_en_retard: number;
    livraisons_30_jours: number;
    montant_engage_ht: string | number;
    otd_global_pct: number | null;
  };
  livraisons: any[];
};

type Maintenance = {
  interventions_ouvertes: number;
  materiels_en_maintenance: number;
  controles_en_retard: number;
  controles_30_jours: number;
  controles: any[];
};

function eur(value: unknown) {
  return Number(value ?? 0).toLocaleString("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  });
}

function nombre(value: unknown) {
  return Number(value ?? 0).toLocaleString("fr-FR", {
    maximumFractionDigits: 3,
  });
}

function dateFr(value: string | null | undefined) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("fr-FR").format(
    new Date(`${value.slice(0, 10)}T12:00:00`)
  );
}

export default function DashboardV2() {
  const { utilisateur } = useAuth();

  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [alertes, setAlertes] = useState<Alertes | null>(null);
  const [achats, setAchats] = useState<Achats | null>(null);
  const [maintenance, setMaintenance] =
    useState<Maintenance | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [chargement, setChargement] = useState(true);
  const [toast, setToast] = useState<any>(null);

  async function charger() {
    setChargement(true);
    const h = entetesAuthentifiees();

    const resultats = await Promise.allSettled([
      apiFetch(`${API}/api/dashboard`, { headers: h }),
      apiFetch(`${API}/api/alertes-logistiques`, { headers: h }),
      apiFetch(`${API}/api/achats/pilotage`, { headers: h }),
      apiFetch(`${API}/api/maintenance-materiel/dashboard`, {
        headers: h,
      }),
      apiFetch(`${API}/api/notifications/me`, { headers: h }),
    ]);

    async function jsonOuNull(index: number) {
      const r = resultats[index];
      if (r.status !== "fulfilled" || !r.value.ok) return null;
      return await r.value.json();
    }

    setDashboard(await jsonOuNull(0));
    setAlertes(await jsonOuNull(1));
    setAchats(await jsonOuNull(2));
    setMaintenance(await jsonOuNull(3));
    setNotifications((await jsonOuNull(4)) ?? []);

    const indisponibles = resultats.filter(
      (r) =>
        r.status === "rejected" ||
        (r.status === "fulfilled" && !r.value.ok)
    ).length;

    if (indisponibles > 0) {
      setToast({
        type: "error",
        message:
          "Certaines données du tableau de bord sont momentanément indisponibles.",
      });
    }

    setChargement(false);
  }

  useEffect(() => {
    charger();
  }, []);

  async function lire(notification: Notification) {
    await apiFetch(`${API}/api/notifications/${notification.id}/lire`, {
      method: "PATCH",
      headers: entetesAuthentifiees(),
    });
    await charger();
  }

  const urgences = useMemo(
    () => (alertes?.alertes ?? []).slice(0, 8),
    [alertes]
  );

  const notificationsNonLues = notifications.filter(
    (n) => !n.lue
  ).length;

  const k = dashboard?.kpis;

  return (
    <div>
      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Pilotage logistique</span>
          <h1>Bonjour {utilisateur.nom_complet}</h1>
          <p>
            Vue consolidée des priorités stocks, achats, préparations et
            matériels.
          </p>
        </div>
        <Button variant="secondary" onClick={charger}>
          <RefreshCcw size={17} />
          Actualiser
        </Button>
      </div>

      <section className={styles.hero}>
        <div className={styles.heroMain}>
          <span>Valeur du stock physique</span>
          <strong>{eur(k?.valeur_stock_physique)}</strong>
          <small>
            {k
              ? `${eur(k.valeur_stock_disponible)} disponible · ${eur(
                  k.valeur_stock_reservee
                )} réservé`
              : chargement
                ? "Chargement…"
                : "Donnée indisponible"}
          </small>
        </div>

        <Link
          href="/alertes"
          className={`${styles.heroTile} ${
            (alertes?.critiques ?? 0) > 0 ? styles.heroCritical : ""
          }`}
        >
          <CircleAlert size={21} />
          <span>Alertes critiques</span>
          <strong>{alertes?.critiques ?? 0}</strong>
          <small>{alertes?.attention ?? 0} à surveiller</small>
        </Link>

        <Link href="/preparations" className={styles.heroTile}>
          <PackageCheck size={21} />
          <span>Préparations à traiter</span>
          <strong>{k?.preparations_a_traiter ?? 0}</strong>
          <small>
            {k?.preparations_en_retard ?? 0} en retard
          </small>
        </Link>

        <Link href="/achats/pilotage" className={styles.heroTile}>
          <Truck size={21} />
          <span>Commandes ouvertes</span>
          <strong>{achats?.kpis.commandes_ouvertes ?? 0}</strong>
          <small>
            {achats?.kpis.commandes_en_retard ?? 0} en retard
          </small>
        </Link>
      </section>

      <section className={styles.kpis}>
        <Kpi
          href="/stocks"
          label="Ruptures"
          value={k?.ruptures ?? 0}
          icon={<PackageX size={20} />}
          tone={(k?.ruptures ?? 0) > 0 ? "critical" : "normal"}
        />
        <Kpi
          href="/reapprovisionnement"
          label="Stocks sous seuil"
          value={k?.stocks_sous_seuil ?? 0}
          icon={<TriangleAlert size={20} />}
          tone={(k?.stocks_sous_seuil ?? 0) > 0 ? "warning" : "normal"}
        />
        <Kpi
          href="/achats/pilotage"
          label="Engagé achats HT"
          value={eur(achats?.kpis.montant_engage_ht)}
          icon={<Euro size={20} />}
        />
        <Kpi
          href="/achats/pilotage"
          label="OTD fournisseurs"
          value={
            achats?.kpis.otd_global_pct == null
              ? "—"
              : `${achats.kpis.otd_global_pct} %`
          }
          icon={<ShieldCheck size={20} />}
        />
        <Kpi
          href="/maintenance-materiel"
          label="Contrôles en retard"
          value={maintenance?.controles_en_retard ?? 0}
          icon={<Wrench size={20} />}
          tone={
            (maintenance?.controles_en_retard ?? 0) > 0
              ? "critical"
              : "normal"
          }
        />
        <Kpi
          href="/maintenance-materiel"
          label="Matériels en maintenance"
          value={maintenance?.materiels_en_maintenance ?? 0}
          icon={<Wrench size={20} />}
        />
        <Kpi
          href="/inventaire/avance"
          label="Inventaires en cours"
          value={k?.inventaires_en_cours ?? 0}
          icon={<ClipboardCheck size={20} />}
        />
        <Kpi
          href="/articles"
          label="Articles actifs"
          value={k?.articles_actifs ?? 0}
          icon={<Boxes size={20} />}
        />
      </section>

      <section className={styles.mainGrid}>
        <article className={`${styles.panel} ${styles.priorityPanel}`}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">À traiter</span>
              <h2>Priorités opérationnelles</h2>
            </div>
            <Link href="/alertes">Toutes les alertes</Link>
          </div>

          <div className={styles.priorityList}>
            {urgences.map((a) => (
              <Link href={a.href} key={a.key} className={styles.priority}>
                <span
                  className={`${styles.level} ${
                    a.niveau === "CRITIQUE"
                      ? styles.levelCritical
                      : a.niveau === "ATTENTION"
                        ? styles.levelWarning
                        : styles.levelInfo
                  }`}
                >
                  {a.niveau}
                </span>
                <div>
                  <strong>{a.titre}</strong>
                  <p>{a.detail}</p>
                </div>
                <span className={styles.category}>{a.categorie}</span>
                <ChevronRight size={17} />
              </Link>
            ))}

            {!urgences.length && (
              <div className={styles.goodState}>
                <Check size={20} />
                <div>
                  <strong>Aucune priorité critique</strong>
                  <span>
                    Le centre d’alertes ne remonte aucune action urgente.
                  </span>
                </div>
              </div>
            )}
          </div>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Approvisionnements</span>
              <h2>Livraisons attendues</h2>
            </div>
            <Link href="/achats/pilotage">Pilotage achats</Link>
          </div>

          <div className={styles.compactList}>
            {(achats?.livraisons ?? []).slice(0, 6).map((x: any) => {
              const retard =
                x.date_livraison_prevue &&
                new Date(`${x.date_livraison_prevue}T23:59:59`) <
                  new Date();

              return (
                <Link
                  href="/achats"
                  className={styles.compactRow}
                  key={x.commande_id}
                >
                  <div>
                    <strong>{x.reference}</strong>
                    <span>{x.fournisseur}</span>
                  </div>
                  <div className={styles.compactRight}>
                    {retard && (
                      <span className={styles.badgeCritical}>
                        En retard
                      </span>
                    )}
                    <b>{dateFr(x.date_livraison_prevue)}</b>
                    <small>{eur(x.montant_restant_ht)} restant</small>
                  </div>
                </Link>
              );
            })}
            {!achats?.livraisons?.length && (
              <p className="muted-text">
                Aucune livraison attendue à court terme.
              </p>
            )}
          </div>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Préparation</span>
              <h2>Commandes à préparer</h2>
            </div>
            <Link href="/preparations">Préparations</Link>
          </div>

          <div className={styles.compactList}>
            {(dashboard?.preparations ?? []).slice(0, 6).map((p: any) => (
              <Link
                href="/preparations"
                className={styles.compactRow}
                key={p.id}
              >
                <div>
                  <strong>{p.reference}</strong>
                  <span>{p.nom}</span>
                </div>
                <div className={styles.compactRight}>
                  {p.en_retard && (
                    <span className={styles.badgeCritical}>
                      En retard
                    </span>
                  )}
                  {p.lignes_bloquees > 0 && (
                    <span className={styles.badgeWarning}>
                      {p.lignes_bloquees} bloquée(s)
                    </span>
                  )}
                  <small>
                    {p.date_besoin
                      ? dateFr(p.date_besoin)
                      : "Sans échéance"}
                  </small>
                </div>
              </Link>
            ))}
            {!dashboard?.preparations?.length && (
              <p className="muted-text">
                Aucune préparation à traiter.
              </p>
            )}
          </div>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Stocks</span>
              <h2>Ruptures & niveaux mini</h2>
            </div>
            <Link href="/stocks">Voir les stocks</Link>
          </div>

          <div className={styles.compactList}>
            {(dashboard?.stocks ?? []).slice(0, 6).map((s: any) => (
              <Link
                href="/stocks"
                className={styles.compactRow}
                key={s.article_id}
              >
                <div>
                  <strong>{s.designation}</strong>
                  <span>{s.reference}</span>
                </div>
                <div className={styles.compactRight}>
                  <span
                    className={
                      s.niveau === "RUPTURE"
                        ? styles.badgeCritical
                        : styles.badgeWarning
                    }
                  >
                    {s.niveau === "RUPTURE" ? "Rupture" : "Sous seuil"}
                  </span>
                  <small>
                    {nombre(s.disponible)} {s.unite} disponible
                  </small>
                </div>
              </Link>
            ))}
            {!dashboard?.stocks?.length && (
              <p className="muted-text">Aucune alerte stock.</p>
            )}
          </div>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Matériel</span>
              <h2>Contrôles & maintenance</h2>
            </div>
            <Link href="/materiels">Module matériels</Link>
          </div>

          <div className={styles.compactList}>
            {(maintenance?.controles ?? []).slice(0, 6).map((m: any) => (
              <Link
                href="/maintenance-materiel"
                className={styles.compactRow}
                key={m.materiel_id}
              >
                <div>
                  <strong>{m.numero_inventaire}</strong>
                  <span>{m.designation}</span>
                </div>
                <div className={styles.compactRight}>
                  <span
                    className={
                      m.statut === "EN_RETARD"
                        ? styles.badgeCritical
                        : styles.badgeWarning
                    }
                  >
                    {m.statut === "EN_RETARD"
                      ? "En retard"
                      : "À venir"}
                  </span>
                  <small>{dateFr(m.date_prochain_controle)}</small>
                </div>
              </Link>
            ))}
            {!maintenance?.controles?.length && (
              <p className="muted-text">
                Aucune échéance matériel dans les 30 jours.
              </p>
            )}
          </div>
        </article>
      </section>

      <section className={styles.bottomGrid}>
        <article className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Traçabilité béton</span>
              <h2>Lots à surveiller</h2>
            </div>
            <Link href="/lots-beton">Lots béton</Link>
          </div>

          <div className={styles.compactList}>
            {(dashboard?.lots ?? []).slice(0, 5).map((lot: any) => (
              <Link
                href="/lots-beton"
                className={styles.compactRow}
                key={lot.lot_id}
              >
                <div>
                  <strong>{lot.article_designation}</strong>
                  <span>
                    {lot.reference_interne} · {lot.numero_lot_fournisseur}
                  </span>
                </div>
                <div className={styles.compactRight}>
                  <span
                    className={
                      lot.jours_restants < 0
                        ? styles.badgeCritical
                        : styles.badgeWarning
                    }
                  >
                    {lot.jours_restants < 0
                      ? `Périmé ${Math.abs(lot.jours_restants)} j`
                      : `${lot.jours_restants} j`}
                  </span>
                  <small>
                    {nombre(lot.quantite_physique)} en stock
                  </small>
                </div>
              </Link>
            ))}
            {!dashboard?.lots?.length && (
              <p className="muted-text">
                Aucun lot à échéance dans les 60 jours.
              </p>
            )}
          </div>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Mes actions</span>
              <h2>Notifications</h2>
            </div>
            <span className={styles.notificationCounter}>
              <Bell size={16} />
              {notificationsNonLues}
            </span>
          </div>

          <div className={styles.notifications}>
            {notifications.slice(0, 6).map((n) => (
              <article
                className={
                  n.lue
                    ? styles.notificationRead
                    : styles.notificationUnread
                }
                key={n.id}
              >
                <PackageCheck size={18} />
                <div>
                  <strong>{n.titre}</strong>
                  <p>{n.message}</p>
                  <small>
                    {new Intl.DateTimeFormat("fr-FR", {
                      dateStyle: "short",
                      timeStyle: "short",
                    }).format(new Date(n.date_creation))}
                  </small>
                </div>
                <div className={styles.notificationActions}>
                  {n.lien && <a href={n.lien}>Ouvrir</a>}
                  {!n.lue && (
                    <button
                      title="Marquer comme lue"
                      onClick={() => lire(n)}
                    >
                      <Check size={14} />
                    </button>
                  )}
                </div>
              </article>
            ))}
            {!notifications.length && (
              <p className="muted-text">
                Aucune notification pour votre compte.
              </p>
            )}
          </div>
        </article>
      </section>

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

function Kpi({
  href,
  label,
  value,
  icon,
  tone = "normal",
}: {
  href: string;
  label: string;
  value: React.ReactNode;
  icon: React.ReactNode;
  tone?: "normal" | "warning" | "critical";
}) {
  return (
    <Link
      href={href}
      className={`${styles.kpi} ${
        tone === "critical"
          ? styles.kpiCritical
          : tone === "warning"
            ? styles.kpiWarning
            : ""
      }`}
    >
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
      <ChevronRight size={15} className={styles.kpiArrow} />
    </Link>
  );
}
