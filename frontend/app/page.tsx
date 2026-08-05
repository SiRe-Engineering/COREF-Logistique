"use client";

import { useEffect, useState } from "react";
import { Bell, Check, PackageCheck } from "lucide-react";
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

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Dashboard() {
  const { utilisateur } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);

  async function chargerNotifications() {
    const response = await fetch(`${API_URL}/api/notifications/me`, {
      headers: entetesAuthentifiees(),
    });

    setNotifications(response.ok ? await response.json() : []);
  }

  useEffect(() => {
    chargerNotifications();
  }, []);

  async function lire(notification: Notification) {
    await fetch(
      `${API_URL}/api/notifications/${notification.id}/lire`,
      {
        method: "PATCH",
        headers: entetesAuthentifiees(),
      }
    );
    await chargerNotifications();
  }

  return (
    <div>
      <div className="page-heading">
        <span className="eyebrow">Vue d’ensemble</span>
        <h1>Bonjour {utilisateur.nom_complet}</h1>
        <p>
          Retrouvez les actions et informations associées à votre compte.
        </p>
      </div>

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
