"use client";

import { useEffect, useState } from "react";

type ApiHealth = {
  status: string;
  database: string;
};

export default function Home() {
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const apiUrl =
      process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

    fetch(`${apiUrl}/api/health`)
      .then((response) => {
        if (!response.ok) throw new Error("API indisponible");
        return response.json();
      })
      .then(setHealth)
      .catch(() => setError(true));
  }, []);

  return (
    <main>
      <h1>Tableau de bord</h1>
      <p className="muted">
        Première version du socle technique de l’application.
      </p>

      <section className="grid">
        <article className="card">
          <h2>Articles</h2>
          <p className="metric">0</p>
          <p className="muted">Références enregistrées</p>
        </article>

        <article className="card">
          <h2>Ruptures</h2>
          <p className="metric">0</p>
          <p className="muted">Articles sous le stock minimum</p>
        </article>

        <article className="card">
          <h2>Matériels</h2>
          <p className="metric">0</p>
          <p className="muted">Équipements suivis</p>
        </article>

        <article className="card">
          <h2>État du système</h2>
          {health && <span className="status">API et base connectées</span>}
          {error && <p>Connexion à l’API impossible.</p>}
          {!health && !error && <p>Vérification en cours…</p>}
        </article>
      </section>
    </main>
  );
}
