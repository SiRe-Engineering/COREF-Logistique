"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type SousFamille = {
  id: number;
  famille_id: number;
  code: string;
  nom: string;
};

type Famille = {
  id: number;
  code: string;
  nom: string;
  sous_familles: SousFamille[];
};

type Article = {
  id: number;
  reference: string;
  designation: string;
  famille_id: number | null;
  sous_famille_id: number | null;
  unite: string;
  stock_minimum: string;
  actif: boolean;
  famille_relation: {
    id: number;
    code: string;
    nom: string;
  } | null;
  sous_famille_relation: {
    id: number;
    code: string;
    nom: string;
  } | null;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialForm = {
  designation: "",
  famille_id: "",
  sous_famille_id: "",
  unite: "unité",
  stock_minimum: "0",
};

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [familles, setFamilles] = useState<Famille[]>([]);
  const [recherche, setRecherche] = useState("");
  const [filtreFamille, setFiltreFamille] = useState("");
  const [modalOuverte, setModalOuverte] = useState(false);
  const [chargement, setChargement] = useState(true);
  const [enregistrement, setEnregistrement] = useState(false);
  const [message, setMessage] = useState("");
  const [erreur, setErreur] = useState("");
  const [form, setForm] = useState(initialForm);

  async function chargerDonnees() {
    setChargement(true);
    setErreur("");

    try {
      const [articlesResponse, famillesResponse] = await Promise.all([
        fetch(`${API_URL}/api/articles`),
        fetch(`${API_URL}/api/familles`),
      ]);

      if (!articlesResponse.ok || !famillesResponse.ok) {
        throw new Error("Chargement impossible");
      }

      const [articlesData, famillesData] = await Promise.all([
        articlesResponse.json(),
        famillesResponse.json(),
      ]);

      setArticles(articlesData);
      setFamilles(famillesData);
    } catch {
      setErreur("Impossible de charger les données depuis l’API.");
    } finally {
      setChargement(false);
    }
  }

  useEffect(() => {
    chargerDonnees();
  }, []);

  const familleSelectionnee = useMemo(
    () =>
      familles.find(
        (famille) => famille.id === Number(form.famille_id)
      ) ?? null,
    [familles, form.famille_id]
  );

  const articlesFiltres = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    return articles.filter((article) => {
      const correspondRecherche =
        !terme ||
        article.reference.toLowerCase().includes(terme) ||
        article.designation.toLowerCase().includes(terme);

      const correspondFamille =
        !filtreFamille ||
        article.famille_id === Number(filtreFamille);

      return correspondRecherche && correspondFamille;
    });
  }, [articles, recherche, filtreFamille]);

  function ouvrirCreation() {
    setForm(initialForm);
    setMessage("");
    setErreur("");
    setModalOuverte(true);
  }

  function fermerCreation() {
    if (!enregistrement) {
      setModalOuverte(false);
    }
  }

  async function creerArticle(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setEnregistrement(true);
    setErreur("");
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/api/articles`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          designation: form.designation,
          famille_id: form.famille_id
            ? Number(form.famille_id)
            : null,
          sous_famille_id: form.sous_famille_id
            ? Number(form.sous_famille_id)
            : null,
          unite: form.unite,
          stock_minimum: Number(form.stock_minimum),
        }),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(
          typeof detail?.detail === "string"
            ? detail.detail
            : "Création impossible."
        );
      }

      const nouvelArticle: Article = await response.json();
      setArticles((actuels) =>
        [...actuels, nouvelArticle].sort((a, b) =>
          a.reference.localeCompare(b.reference)
        )
      );
      setMessage(
        `Article créé avec la référence ${nouvelArticle.reference}.`
      );
      setForm(initialForm);

      window.setTimeout(() => {
        setModalOuverte(false);
        setMessage("");
      }, 1200);
    } catch (cause) {
      setErreur(
        cause instanceof Error
          ? cause.message
          : "Une erreur inattendue est survenue."
      );
    } finally {
      setEnregistrement(false);
    }
  }

  async function archiverArticle(article: Article) {
    const confirmation = window.confirm(
      `Archiver ${article.reference} — ${article.designation} ?`
    );
    if (!confirmation) return;

    setErreur("");

    try {
      const response = await fetch(
        `${API_URL}/api/articles/${article.id}`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        throw new Error("Archivage impossible.");
      }

      setArticles((actuels) =>
        actuels.filter((element) => element.id !== article.id)
      );
    } catch (cause) {
      setErreur(
        cause instanceof Error
          ? cause.message
          : "Une erreur inattendue est survenue."
      );
    }
  }

  return (
    <div>
      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Référentiel</span>
          <h1>Articles</h1>
          <p>
            Gérez les références internes, leurs familles et leurs paramètres
            logistiques.
          </p>
        </div>

        <button className="primary-button" onClick={ouvrirCreation}>
          <span>＋</span>
          Nouvel article
        </button>
      </div>

      {erreur && <div className="alert alert-error">{erreur}</div>}

      <section className="content-card">
        <div className="filters-row">
          <label className="search-field">
            <span>⌕</span>
            <input
              type="search"
              placeholder="Rechercher une référence ou une désignation"
              value={recherche}
              onChange={(event) => setRecherche(event.target.value)}
            />
          </label>

          <select
            value={filtreFamille}
            onChange={(event) => setFiltreFamille(event.target.value)}
            aria-label="Filtrer par famille"
          >
            <option value="">Toutes les familles</option>
            {familles.map((famille) => (
              <option key={famille.id} value={famille.id}>
                {famille.nom}
              </option>
            ))}
          </select>

          <span className="result-count">
            {articlesFiltres.length} article
            {articlesFiltres.length > 1 ? "s" : ""}
          </span>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Référence</th>
                <th>Désignation</th>
                <th>Famille</th>
                <th>Sous-famille</th>
                <th>Unité</th>
                <th>Stock mini</th>
                <th>Statut</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {chargement && (
                <tr>
                  <td colSpan={8} className="empty-state">
                    Chargement des articles…
                  </td>
                </tr>
              )}

              {!chargement &&
                articlesFiltres.map((article) => (
                  <tr key={article.id}>
                    <td>
                      <span className="reference-chip">
                        {article.reference}
                      </span>
                    </td>
                    <td>
                      <strong>{article.designation}</strong>
                    </td>
                    <td>{article.famille_relation?.nom ?? "—"}</td>
                    <td>{article.sous_famille_relation?.nom ?? "—"}</td>
                    <td>{article.unite}</td>
                    <td>{Number(article.stock_minimum).toLocaleString("fr-FR")}</td>
                    <td>
                      <span className="status-pill status-active">Actif</span>
                    </td>
                    <td className="table-actions">
                      <button
                        className="icon-button danger-button"
                        title="Archiver l’article"
                        onClick={() => archiverArticle(article)}
                      >
                        ×
                      </button>
                    </td>
                  </tr>
                ))}

              {!chargement && articlesFiltres.length === 0 && (
                <tr>
                  <td colSpan={8} className="empty-state">
                    <strong>Aucun article trouvé</strong>
                    <span>
                      Modifiez les filtres ou créez une nouvelle référence.
                    </span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {modalOuverte && (
        <div className="modal-backdrop" onMouseDown={fermerCreation}>
          <section
            className="modal-card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">Nouvelle référence</span>
                <h2 id="modal-title">Créer un article</h2>
                <p>
                  La référence interne sera attribuée automatiquement.
                </p>
              </div>
              <button
                className="icon-button"
                onClick={fermerCreation}
                aria-label="Fermer"
              >
                ×
              </button>
            </div>

            <form onSubmit={creerArticle}>
              <div className="generated-reference">
                <span>Référence interne</span>
                <strong>ART-XXXXXX</strong>
                <small>Générée après l’enregistrement</small>
              </div>

              <div className="form-grid">
                <label className="field field-wide">
                  <span>Désignation *</span>
                  <input
                    required
                    maxLength={255}
                    autoFocus
                    placeholder="Ex. Béton dense 70 % alumine"
                    value={form.designation}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        designation: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Famille</span>
                  <select
                    value={form.famille_id}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        famille_id: event.target.value,
                        sous_famille_id: "",
                      })
                    }
                  >
                    <option value="">Sélectionner</option>
                    {familles.map((famille) => (
                      <option key={famille.id} value={famille.id}>
                        {famille.nom}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Sous-famille</span>
                  <select
                    value={form.sous_famille_id}
                    disabled={!familleSelectionnee}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        sous_famille_id: event.target.value,
                      })
                    }
                  >
                    <option value="">Sélectionner</option>
                    {familleSelectionnee?.sous_familles.map(
                      (sousFamille) => (
                        <option
                          key={sousFamille.id}
                          value={sousFamille.id}
                        >
                          {sousFamille.nom}
                        </option>
                      )
                    )}
                  </select>
                </label>

                <label className="field">
                  <span>Unité *</span>
                  <select
                    required
                    value={form.unite}
                    onChange={(event) =>
                      setForm({ ...form, unite: event.target.value })
                    }
                  >
                    <option value="unité">Unité</option>
                    <option value="pièce">Pièce</option>
                    <option value="sac">Sac</option>
                    <option value="kg">Kilogramme</option>
                    <option value="tonne">Tonne</option>
                    <option value="m">Mètre</option>
                    <option value="m²">Mètre carré</option>
                    <option value="m³">Mètre cube</option>
                    <option value="litre">Litre</option>
                    <option value="rouleau">Rouleau</option>
                    <option value="boîte">Boîte</option>
                    <option value="carton">Carton</option>
                    <option value="palette">Palette</option>
                    <option value="paquet">Paquet</option>
                  </select>
                </label>

                <label className="field">
                  <span>Stock minimum</span>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={form.stock_minimum}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        stock_minimum: event.target.value,
                      })
                    }
                  />
                </label>
              </div>

              {message && <div className="alert alert-success">{message}</div>}
              {erreur && <div className="alert alert-error">{erreur}</div>}

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={fermerCreation}
                  disabled={enregistrement}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={enregistrement}
                >
                  {enregistrement ? "Création…" : "Créer l’article"}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
