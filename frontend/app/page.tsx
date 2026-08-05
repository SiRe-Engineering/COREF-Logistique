"use client";

import { useEffect, useState } from "react";
import {
  Bell,
  Check,
  PackageCheck,
} from "lucide-react";
import styles from "./page.module.css";

type ApiHealth = {
  status: string;
  database: string;
  version: string;
};

type Article = { id: number };
type Materiel = { id: number };

type StockResume = {
  ruptures: number;
};

type Notification = {
  id: number;
  titre: string;
  message: string;
  type: string;
  lien: string | null;
  lue: boolean;
  date_creation: string;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Dashboard() {
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [articles, setArticles] = useState<Article[]>([]);
  const [materiels, setMateriels] = useState<Materiel[]>([]);
  const [stockResume, setStockResume] = useState<StockResume>({
    ruptures: 0,
  });
  const [utilisateur, setUtilisateur] = useState("");
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    const utilisateurLocal =
      localStorage.getItem("coref-current-user") ?? "Utilisateur local";
    setUtilisateur(utilisateurLocal);

    Promise.all([
      fetch(`${API_URL}/api/health`).then((response) => response.json()),
      fetch(`${API_URL}/api/articles`).then((response) => response.json()),
      fetch(`${API_URL}/api/materiels`).then((response) => response.json()),
      fetch(`${API_URL}/api/stocks/resume`).then((response) =>
        response.json()
      ),
    ]).then(([healthData, articleData, materielData, resumeData]) => {
      setHealth(healthData);
      setArticles(articleData);
      setMateriels(materielData);
      setStockResume(resumeData);
    });
  }, []);

  useEffect(() => {
    if (!utilisateur) return;

    localStorage.setItem("coref-current-user", utilisateur);
    fetch(
      `${API_URL}/api/notifications?destinataire=${encodeURIComponent(
        utilisateur
      )}`
    )
      .then((response) => response.json())
      .then(setNotifications)
      .catch(() => setNotifications([]));
  }, [utilisateur]);

  async function lire(notification: Notification) {
    await fetch(
      `${API_URL}/api/notifications/${notification.id}/lire`,
      { method: "PATCH" }
    );
    setNotifications((actuelles) =>
      actuelles.map((element) =>
        element.id === notification.id
          ? { ...element, lue: true }
          : element
      )
    );
  }

  return (
    <div>
      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Vue d’ensemble</span>
          <h1>Tableau de bord</h1>
          <p>Suivez les indicateurs et les actions qui vous concernent.</p>
        </div>

        <label className={styles.userSelector}>
          <span>Utilisateur affiché</span>
          <input
            value={utilisateur}
            onChange={(event) => setUtilisateur(event.target.value)}
            placeholder="Nom exact de l’utilisateur"
          />
        </label>
      </div>

      <section className="metrics-grid">
        <article className="metric-card">
          <span className="metric-label">Articles actifs</span>
          <strong>{articles.length}</strong>
          <small>Références enregistrées</small>
        </article>

        <article className="metric-card">
          <span className="metric-label">Ruptures</span>
          <strong>{stockResume.ruptures}</strong>
          <small>Articles sans stock disponible</small>
        </article>

        <article className="metric-card">
          <span className="metric-label">Matériels</span>
          <strong>{materiels.length}</strong>
          <small>Équipements suivis</small>
        </article>

        <article className="metric-card">
          <span className="metric-label">État du système</span>
          <strong className="status-text">
            {health ? "Opérationnel" : "Vérification…"}
          </strong>
          <small>
            {health
              ? `API ${health.version} et base connectées`
              : "Connexion en cours"}
          </small>
        </article>
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
              Aucune notification pour « {utilisateur} ».
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
