"use client";

import { useEffect, useState } from "react";

type ApiHealth = {
  status: string;
  database: string;
  version: string;
};

type Article = {
  id: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Dashboard() {
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [articles, setArticles] = useState<Article[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/health`).then((response) => response.json()),
      fetch(`${API_URL}/api/articles`).then((response) => response.json()),
    ])
      .then(([healthData, articleData]) => {
        setHealth(healthData);
        setArticles(articleData);
      })
      .catch(() => setError(true));
  }, []);

  return (
    <div>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Vue d’ensemble</span>
          <h1>Tableau de bord</h1>
          <p>Suivez les principaux indicateurs de COREF Logistique.</p>
        </div>
      </div>

      <section className="metrics-grid">
        <article className="metric-card">
          <span className="metric-label">Articles actifs</span>
          <strong>{articles.length}</strong>
          <small>Références enregistrées</small>
        </article>

        <article className="metric-card">
          <span className="metric-label">Ruptures</span>
          <strong>0</strong>
          <small>Calcul disponible avec le module Stock</small>
        </article>

        <article className="metric-card">
          <span className="metric-label">Matériels</span>
          <strong>0</strong>
          <small>Module à venir</small>
        </article>

        <article className="metric-card">
          <span className="metric-label">État du système</span>
          {health && (
            <>
              <strong className="status-text">Opérationnel</strong>
              <small>API {health.version} et base connectées</small>
            </>
          )}
          {error && (
            <>
              <strong className="status-text status-error">Indisponible</strong>
              <small>Connexion au backend impossible</small>
            </>
          )}
          {!health && !error && <small>Vérification en cours…</small>}
        </article>
      </section>

      <section className="content-card welcome-card">
        <div>
          <span className="eyebrow">Sprint UI V1</span>
          <h2>Le référentiel Articles est disponible</h2>
          <p>
            Créez vos premières références avec génération automatique,
            classement par famille et sous-famille, puis retrouvez-les grâce
            à la recherche et aux filtres.
          </p>
        </div>
        <a className="primary-button" href="/articles">
          Ouvrir les articles
        </a>
      </section>
    </div>
  );
}
