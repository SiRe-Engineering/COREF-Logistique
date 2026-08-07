"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  AlertTriangle,
  Bell,
  Boxes,
  Check,
  ClipboardCheck,
  Clock3,
  PackageCheck,
  PackageX,
  RotateCcw,
  TriangleAlert,
} from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import { entetesAuthentifiees } from "@/lib/auth";
import styles from "./page.module.css";

type Notification = {
  id: number;
  titre: string;
  message: string;
  lien: string | null;
  lue: boolean;
  date_creation: string;
};

type DashboardData = {
  date_reference: string;
  kpis: {
    articles_actifs: number;
    ruptures: number;
    stocks_sous_seuil: number;
    lots_a_perimer: number;
    preparations_a_traiter: number;
    preparations_en_retard: number;
    inventaires_en_cours: number;
    retours_en_attente: number;
  };
  stocks: Array<{
    article_id: number;
    reference: string;
    designation: string;
    unite: string;
    disponible: string;
    seuil: string;
    niveau: string;
  }>;
  lots: Array<{
    lot_id: number;
    reference_interne: string;
    numero_lot_fournisseur: string;
    article_reference: string;
    article_designation: string;
    date_peremption: string;
    jours_restants: number;
    quantite_physique: string;
    niveau: string;
  }>;
  preparations: Array<{
    id: number;
    reference: string;
    nom: string;
    statut: string;
    date_besoin: string | null;
    demandeur: string | null;
    preparateur: string | null;
    en_retard: boolean;
    lignes_bloquees: number;
  }>;
  inventaires: Array<{
    id: number;
    reference: string;
    nom: string;
    operateur: string | null;
    lignes_total: number;
    lignes_comptees: number;
  }>;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function nombre(value: string) {
  return Number(value).toLocaleString("fr-FR", {
    maximumFractionDigits: 3,
  });
}

export default function Dashboard() {
  const { utilisateur } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);

  async function charger() {
    const [notificationsResponse, dashboardResponse] = await Promise.all([
      fetch(`${API_URL}/api/notifications/me`, {
        headers: entetesAuthentifiees(),
      }),
      fetch(`${API_URL}/api/dashboard`, {
        headers: entetesAuthentifiees(),
      }),
    ]);

    setNotifications(
      notificationsResponse.ok
        ? await notificationsResponse.json()
        : []
    );
    setDashboard(
      dashboardResponse.ok ? await dashboardResponse.json() : null
    );
  }

  useEffect(() => {
    charger();
  }, []);

  async function lire(notification: Notification) {
    await fetch(
      `${API_URL}/api/notifications/${notification.id}/lire`,
      {
        method: "PATCH",
        headers: entetesAuthentifiees(),
      }
    );
    await charger();
  }

  const kpis = dashboard?.kpis;

  return (
    <div>
      <div className="page-heading">
        <span className="eyebrow">Pilotage logistique</span>
        <h1>Bonjour {utilisateur.nom_complet}</h1>
        <p>
          Priorités, alertes et activité opérationnelle de COREF Logistique.
        </p>
      </div>

      {kpis && (
        <section className={styles.kpis}>
          <Kpi
            label="Ruptures"
            value={kpis.ruptures}
            icon={<PackageX size={22} />}
            critical={kpis.ruptures > 0}
          />
          <Kpi
            label="Sous seuil"
            value={kpis.stocks_sous_seuil}
            icon={<TriangleAlert size={22} />}
            warning={kpis.stocks_sous_seuil > 0}
          />
          <Kpi
            label="Préparations à traiter"
            value={kpis.preparations_a_traiter}
            icon={<PackageCheck size={22} />}
          />
          <Kpi
            label="Préparations en retard"
            value={kpis.preparations_en_retard}
            icon={<Clock3 size={22} />}
            critical={kpis.preparations_en_retard > 0}
          />
          <Kpi
            label="Lots ≤ 60 jours"
            value={kpis.lots_a_perimer}
            icon={<AlertTriangle size={22} />}
            warning={kpis.lots_a_perimer > 0}
          />
          <Kpi
            label="Inventaires en cours"
            value={kpis.inventaires_en_cours}
            icon={<ClipboardCheck size={22} />}
          />
          <Kpi
            label="Lignes expédiées non retournées"
            value={kpis.retours_en_attente}
            icon={<RotateCcw size={22} />}
          />
          <Kpi
            label="Articles actifs"
            value={kpis.articles_actifs}
            icon={<Boxes size={22} />}
          />
        </section>
      )}

      <section className={styles.dashboardGrid}>
        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">À traiter aujourd’hui</span>
              <h2>Préparations</h2>
            </div>
            <Link href="/preparations">Tout ouvrir</Link>
          </div>
          <div className={styles.list}>
            {dashboard?.preparations.map((preparation) => (
              <Link
                href="/preparations"
                className={styles.row}
                key={preparation.id}
              >
                <div>
                  <strong>{preparation.reference}</strong>
                  <span>{preparation.nom}</span>
                </div>
                <div className={styles.rowRight}>
                  {preparation.en_retard && (
                    <span className={styles.criticalBadge}>En retard</span>
                  )}
                  {preparation.lignes_bloquees > 0 && (
                    <span className={styles.warningBadge}>
                      {preparation.lignes_bloquees} bloquée(s)
                    </span>
                  )}
                  <small>
                    {preparation.date_besoin
                      ? new Date(
                          `${preparation.date_besoin}T12:00:00`
                        ).toLocaleDateString("fr-FR")
                      : "Sans échéance"}
                  </small>
                </div>
              </Link>
            ))}
            {dashboard?.preparations.length === 0 && (
              <p className="muted-text">Aucune préparation à traiter.</p>
            )}
          </div>
        </div>

        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Stock</span>
              <h2>Ruptures & seuils</h2>
            </div>
            <Link href="/stocks">Stocks</Link>
          </div>
          <div className={styles.list}>
            {dashboard?.stocks.map((stock) => (
              <Link
                href="/stocks"
                className={styles.row}
                key={stock.article_id}
              >
                <div>
                  <strong>{stock.designation}</strong>
                  <span>{stock.reference}</span>
                </div>
                <div className={styles.rowRight}>
                  <span
                    className={
                      stock.niveau === "RUPTURE"
                        ? styles.criticalBadge
                        : styles.warningBadge
                    }
                  >
                    {stock.niveau === "RUPTURE"
                      ? "Rupture"
                      : "Sous seuil"}
                  </span>
                  <small>
                    {nombre(stock.disponible)} {stock.unite} disponible
                  </small>
                </div>
              </Link>
            ))}
            {dashboard?.stocks.length === 0 && (
              <p className="muted-text">Aucune alerte stock.</p>
            )}
          </div>
        </div>

        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Traçabilité béton</span>
              <h2>Péremptions</h2>
            </div>
            <Link href="/lots-beton">Lots béton</Link>
          </div>
          <div className={styles.list}>
            {dashboard?.lots.map((lot) => (
              <Link
                href="/lots-beton"
                className={styles.row}
                key={lot.lot_id}
              >
                <div>
                  <strong>{lot.article_designation}</strong>
                  <span>
                    {lot.reference_interne} · {lot.numero_lot_fournisseur}
                  </span>
                </div>
                <div className={styles.rowRight}>
                  <span
                    className={
                      lot.niveau === "A_SURVEILLER"
                        ? styles.warningBadge
                        : styles.criticalBadge
                    }
                  >
                    {lot.jours_restants < 0
                      ? `Périmé ${Math.abs(lot.jours_restants)} j`
                      : `${lot.jours_restants} j`}
                  </span>
                  <small>{nombre(lot.quantite_physique)} en stock</small>
                </div>
              </Link>
            ))}
            {dashboard?.lots.length === 0 && (
              <p className="muted-text">
                Aucun lot à échéance dans les 60 jours.
              </p>
            )}
          </div>
        </div>

        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span className="eyebrow">Comptages</span>
              <h2>Inventaires en cours</h2>
            </div>
            <Link href="/inventaires">Inventaires</Link>
          </div>
          <div className={styles.list}>
            {dashboard?.inventaires.map((inventaire) => (
              <Link
                href="/inventaires"
                className={styles.row}
                key={inventaire.id}
              >
                <div>
                  <strong>{inventaire.nom}</strong>
                  <span>{inventaire.reference}</span>
                </div>
                <div className={styles.rowRight}>
                  <small>
                    {inventaire.lignes_comptees} / {inventaire.lignes_total}
                    {" "}comptées
                  </small>
                </div>
              </Link>
            ))}
            {dashboard?.inventaires.length === 0 && (
              <p className="muted-text">Aucun inventaire en cours.</p>
            )}
          </div>
        </div>
      </section>

      <section className={styles.notificationsCard}>
        <div className={styles.notificationsHeader}>
          <div>
            <span className="eyebrow">Mes actions</span>
            <h2>Notifications</h2>
          </div>
          <div className={styles.notificationCount}>
            <Bell size={17} />
            {notifications.filter((notification) => !notification.lue).length}
          </div>
        </div>

        <div className={styles.notifications}>
          {notifications.map((notification) => (
            <article
              key={notification.id}
              className={
                notification.lue
                  ? styles.notificationRead
                  : styles.notificationUnread
              }
            >
              <PackageCheck size={19} />
              <div>
                <strong>{notification.titre}</strong>
                <p>{notification.message}</p>
                <small>
                  {new Intl.DateTimeFormat("fr-FR", {
                    dateStyle: "short",
                    timeStyle: "short",
                  }).format(new Date(notification.date_creation))}
                </small>
              </div>
              <div className={styles.notificationActions}>
                {notification.lien && (
                  <a href={notification.lien}>Ouvrir</a>
                )}
                {!notification.lue && (
                  <button onClick={() => lire(notification)}>
                    <Check size={15} />
                  </button>
                )}
              </div>
            </article>
          ))}
          {notifications.length === 0 && (
            <p className="muted-text">
              Aucune notification pour votre compte.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}

function Kpi({
  label,
  value,
  icon,
  critical = false,
  warning = false,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  critical?: boolean;
  warning?: boolean;
}) {
  return (
    <article
      className={`${styles.kpi} ${
        critical
          ? styles.kpiCritical
          : warning
            ? styles.kpiWarning
            : ""
      }`}
    >
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
