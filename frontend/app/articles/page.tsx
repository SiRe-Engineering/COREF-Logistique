"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  PackagePlus,
  Search,
  Trash2,
  Printer,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Toast } from "@/components/ui/Toast";

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
  cout_unitaire_moyen: string;
  dernier_prix_achat: string | null;
  date_maj_cout: string | null;
  actif: boolean;
  famille_relation: { id: number; code: string; nom: string } | null;
  sous_famille_relation: { id: number; code: string; nom: string } | null;
};

type SortKey = "reference" | "designation" | "famille" | "stock_minimum";
type SortDirection = "asc" | "desc";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialForm = {
  designation: "",
  famille_id: "",
  sous_famille_id: "",
  unite: "unité",
  stock_minimum: "0",
  cout_unitaire_moyen: "0",
};

function familleTone(nom: string | undefined) {
  if (nom === "Béton") return "beton" as const;
  if (nom === "Isolants") return "isolants" as const;
  return "neutral" as const;
}

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [familles, setFamilles] = useState<Famille[]>([]);
  const [recherche, setRecherche] = useState("");
  const [filtreFamille, setFiltreFamille] = useState("");
  const [modalOuverte, setModalOuverte] = useState(false);
  const [articleSelectionne, setArticleSelectionne] = useState<Article | null>(null);
  const [chargement, setChargement] = useState(true);
  const [enregistrement, setEnregistrement] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("reference");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);
  const [form, setForm] = useState(initialForm);

  async function chargerDonnees() {
    setChargement(true);
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
      setToast({
        type: "error",
        message: "Impossible de charger les données depuis l’API.",
      });
    } finally {
      setChargement(false);
    }
  }

  useEffect(() => {
    chargerDonnees();
  }, []);

  const familleSelectionnee = useMemo(
    () =>
      familles.find((famille) => famille.id === Number(form.famille_id)) ?? null,
    [familles, form.famille_id]
  );

  const articlesFiltres = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    const filtres = articles.filter((article) => {
      const correspondRecherche =
        !terme ||
        article.reference.toLowerCase().includes(terme) ||
        article.designation.toLowerCase().includes(terme);

      const correspondFamille =
        !filtreFamille || article.famille_id === Number(filtreFamille);

      return correspondRecherche && correspondFamille;
    });

    return [...filtres].sort((a, b) => {
      let valeurA: string | number = "";
      let valeurB: string | number = "";

      if (sortKey === "reference") {
        valeurA = a.reference;
        valeurB = b.reference;
      } else if (sortKey === "designation") {
        valeurA = a.designation;
        valeurB = b.designation;
      } else if (sortKey === "famille") {
        valeurA = a.famille_relation?.nom ?? "";
        valeurB = b.famille_relation?.nom ?? "";
      } else {
        valeurA = Number(a.stock_minimum);
        valeurB = Number(b.stock_minimum);
      }

      const resultat =
        typeof valeurA === "number" && typeof valeurB === "number"
          ? valeurA - valeurB
          : String(valeurA).localeCompare(String(valeurB), "fr");

      return sortDirection === "asc" ? resultat : -resultat;
    });
  }, [articles, recherche, filtreFamille, sortKey, sortDirection]);

  function changerTri(cle: SortKey) {
    if (sortKey === cle) {
      setSortDirection((direction) => (direction === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(cle);
      setSortDirection("asc");
    }
  }

  function SortIcon({ cle }: { cle: SortKey }) {
    if (sortKey !== cle) return <ArrowUpDown size={14} />;
    return sortDirection === "asc" ? (
      <ArrowUp size={14} />
    ) : (
      <ArrowDown size={14} />
    );
  }

  async function creerArticle(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setEnregistrement(true);

    try {
      const response = await fetch(`${API_URL}/api/articles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          designation: form.designation,
          famille_id: form.famille_id ? Number(form.famille_id) : null,
          sous_famille_id: form.sous_famille_id
            ? Number(form.sous_famille_id)
            : null,
          unite: form.unite,
          stock_minimum: Number(form.stock_minimum),
          cout_unitaire_moyen: Number(
            form.cout_unitaire_moyen.replace(",", ".")
          ),
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
      setArticles((actuels) => [...actuels, nouvelArticle]);
      setForm(initialForm);
      setModalOuverte(false);
      setToast({
        type: "success",
        message: `Article ${nouvelArticle.reference} créé.`,
      });
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Une erreur inattendue est survenue.",
      });
    } finally {
      setEnregistrement(false);
    }
  }

  async function archiverArticle(article: Article) {
    if (!window.confirm(`Archiver ${article.reference} ?`)) return;

    try {
      const response = await fetch(`${API_URL}/api/articles/${article.id}`, {
        method: "DELETE",
      });
      if (!response.ok) throw new Error("Archivage impossible.");

      setArticles((actuels) =>
        actuels.filter((element) => element.id !== article.id)
      );
      setArticleSelectionne(null);
      setToast({
        type: "success",
        message: `${article.reference} a été archivé.`,
      });
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Une erreur inattendue est survenue.",
      });
    }
  }


  async function definirCump(article: Article) {
    const saisie = window.prompt(
      `CUMP initial / corrigé pour ${article.reference} (€ / ${article.unite}) :`,
      article.cout_unitaire_moyen ?? "0"
    );
    if (saisie === null) return;

    const cout = Number(saisie.replace(",", "."));
    if (!Number.isFinite(cout) || cout < 0) {
      setToast({
        type: "error",
        message: "Le coût unitaire est invalide.",
      });
      return;
    }

    const response = await fetch(
      `${API_URL}/api/articles/${article.id}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cout_unitaire_moyen: cout }),
      }
    );
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      setToast({
        type: "error",
        message:
          typeof data?.detail === "string"
            ? data.detail
            : "Mise à jour du CUMP impossible.",
      });
      return;
    }

    setArticleSelectionne(data);
    setArticles((actuels) =>
      actuels.map((item) => item.id === data.id ? data : item)
    );
    setToast({
      type: "success",
      message: `CUMP de ${data.reference} mis à jour.`,
    });
  }

  return (
    <div>
      <div className="breadcrumb">Référentiel / Articles</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Référentiel</span>
          <h1>Articles</h1>
          <p>Gérez les références internes et leurs paramètres logistiques.</p>
        </div>

        <Button variant="secondary" onClick={() => setModalOuverte(true)}>
          <PackagePlus size={18} />
          Nouvel article
        </Button>
      </div>

      <section className="content-card">
        <div className="filters-row">
          <label className="search-field">
            <Search size={17} />
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
                <th>
                  <button className="sort-button" onClick={() => changerTri("reference")}>
                    Référence <SortIcon cle="reference" />
                  </button>
                </th>
                <th>
                  <button className="sort-button" onClick={() => changerTri("designation")}>
                    Désignation <SortIcon cle="designation" />
                  </button>
                </th>
                <th>
                  <button className="sort-button" onClick={() => changerTri("famille")}>
                    Famille <SortIcon cle="famille" />
                  </button>
                </th>
                <th>Sous-famille</th>
                <th>Unité</th>
                <th>
                  <button className="sort-button" onClick={() => changerTri("stock_minimum")}>
                    Stock mini <SortIcon cle="stock_minimum" />
                  </button>
                </th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {chargement && (
                <tr>
                  <td colSpan={7} className="empty-state">
                    Chargement des articles…
                  </td>
                </tr>
              )}

              {!chargement &&
                articlesFiltres.map((article) => (
                  <tr
                    key={article.id}
                    className="clickable-row"
                    onClick={() => setArticleSelectionne(article)}
                  >
                    <td>
                      <span className="reference-chip">{article.reference}</span>
                    </td>
                    <td><strong>{article.designation}</strong></td>
                    <td>
                      {article.famille_relation ? (
                        <Badge tone={familleTone(article.famille_relation.nom)}>
                          {article.famille_relation.nom}
                        </Badge>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>{article.sous_famille_relation?.nom ?? "—"}</td>
                    <td>{article.unite}</td>
                    <td>{Number(article.stock_minimum).toLocaleString("fr-FR")}</td>
                    <td><Badge tone="success">Actif</Badge></td>
                  </tr>
                ))}

              {!chargement && articlesFiltres.length === 0 && (
                <tr>
                  <td colSpan={7} className="empty-state">
                    <strong>Aucun article trouvé</strong>
                    <span>Modifiez les filtres ou créez une référence.</span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <Drawer
        open={articleSelectionne !== null}
        title={articleSelectionne?.reference ?? ""}
        onClose={() => setArticleSelectionne(null)}
      >
        {articleSelectionne && (
          <div className="article-detail">
            <div className="article-detail-title">
              <h3>{articleSelectionne.designation}</h3>
              <Badge tone="success">Actif</Badge>
            </div>

            <dl className="detail-grid">
              <div><dt>Famille</dt><dd>{articleSelectionne.famille_relation?.nom ?? "—"}</dd></div>
              <div><dt>Sous-famille</dt><dd>{articleSelectionne.sous_famille_relation?.nom ?? "—"}</dd></div>
              <div><dt>Unité</dt><dd>{articleSelectionne.unite}</dd></div>
              <div><dt>Stock minimum</dt><dd>{articleSelectionne.stock_minimum}</dd></div>
              <div>
                <dt>CUMP</dt>
                <dd>
                  {Number(articleSelectionne.cout_unitaire_moyen)
                    .toLocaleString("fr-FR", {
                      style: "currency",
                      currency: "EUR",
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 4,
                    })} / {articleSelectionne.unite}
                </dd>
              </div>
              <div>
                <dt>Dernier prix d’achat</dt>
                <dd>
                  {articleSelectionne.dernier_prix_achat === null
                    ? "—"
                    : Number(articleSelectionne.dernier_prix_achat)
                        .toLocaleString("fr-FR", {
                          style: "currency",
                          currency: "EUR",
                        })}
                </dd>
              </div>
            </dl>

            <section className="drawer-section">
              <h4>Identification</h4>
              <Button
                variant="secondary"
                onClick={() =>
                  window.open(
                    `/articles/${articleSelectionne.id}/etiquette`,
                    "_blank",
                    "noopener,noreferrer"
                  )
                }
              >
                <Printer size={17} />
                Imprimer l’étiquette QR
              </Button>
            </section>

            <section className="drawer-section">
              <h4>Valorisation</h4>
              <Button
                variant="secondary"
                onClick={() => definirCump(articleSelectionne)}
              >
                Définir / corriger le CUMP
              </Button>
            </section>

            <section className="drawer-section">
              <h4>Stock</h4>
              <div className="placeholder-panel">
                Les quantités par emplacement seront disponibles avec le module Stock.
              </div>
            </section>

            <section className="drawer-section">
              <h4>Documents</h4>
              <div className="placeholder-panel">
                Aucun document associé pour le moment.
              </div>
            </section>

            <div className="drawer-actions">
              <Button
                variant="danger"
                onClick={() => archiverArticle(articleSelectionne)}
              >
                <Trash2 size={17} />
                Archiver l’article
              </Button>
            </div>
          </div>
        )}
      </Drawer>

      {modalOuverte && (
        <div className="modal-backdrop" onMouseDown={() => setModalOuverte(false)}>
          <section
            className="modal-card"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">Nouvelle référence</span>
                <h2>Créer un article</h2>
                <p>La référence sera attribuée automatiquement.</p>
              </div>
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
                    autoFocus
                    value={form.designation}
                    onChange={(event) =>
                      setForm({ ...form, designation: event.target.value })
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
                      setForm({ ...form, sous_famille_id: event.target.value })
                    }
                  >
                    <option value="">Sélectionner</option>
                    {familleSelectionnee?.sous_familles.map((sf) => (
                      <option key={sf.id} value={sf.id}>{sf.nom}</option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Unité *</span>
                  <select
                    value={form.unite}
                    onChange={(event) =>
                      setForm({ ...form, unite: event.target.value })
                    }
                  >
                    {["unité","pièce","sac","kg","tonne","m","m²","m³","litre","rouleau","boîte","carton","palette","paquet"].map(
                      (unite) => <option key={unite} value={unite}>{unite}</option>
                    )}
                  </select>
                </label>

                <label className="field">
                  <span>CUMP initial (€ / unité)</span>
                  <input
                    inputMode="decimal"
                    value={form.cout_unitaire_moyen}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        cout_unitaire_moyen: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Stock minimum</span>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={form.stock_minimum}
                    onChange={(event) =>
                      setForm({ ...form, stock_minimum: event.target.value })
                    }
                  />
                </label>
              </div>

              <div className="modal-actions">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setModalOuverte(false)}
                >
                  Annuler
                </Button>
                <Button type="submit" disabled={enregistrement}>
                  {enregistrement ? "Création…" : "Créer l’article"}
                </Button>
              </div>
            </form>
          </section>
        </div>
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
