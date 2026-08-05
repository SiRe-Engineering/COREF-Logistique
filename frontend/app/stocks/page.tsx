"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Boxes,
  CircleGauge,
  PackageCheck,
  Plus,
  Search,
  Warehouse,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";

type Article = {
  id: number;
  reference: string;
  designation: string;
  unite: string;
  stock_minimum: string;
  stock_maximum: string;
  seuil_alerte: string;
};

type Emplacement = {
  id: number;
  code: string;
  nom: string;
  type: string;
};

type Stock = {
  id: number;
  article_id: number;
  emplacement_id: number;
  quantite_physique: string;
  quantite_reservee: string;
  quantite_disponible: string;
  date_modification: string;
  article: Article;
  emplacement: Emplacement;
};

type Resume = {
  lignes_stock: number;
  articles_stockes: number;
  ruptures: number;
  alertes: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialForm = {
  article_id: "",
  emplacement_id: "",
  quantite_physique: "0",
  quantite_reservee: "0",
};

function statutStock(stock: Stock) {
  const disponible = Number(stock.quantite_disponible);
  const seuil = Math.max(
    Number(stock.article.stock_minimum),
    Number(stock.article.seuil_alerte)
  );

  if (disponible <= 0) return { label: "Rupture", tone: "beton" as const };
  if (disponible <= seuil) return { label: "Alerte", tone: "warning" as const };
  return { label: "Disponible", tone: "success" as const };
}

export default function StocksPage() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [resume, setResume] = useState<Resume>({
    lignes_stock: 0,
    articles_stockes: 0,
    ruptures: 0,
    alertes: 0,
  });
  const [recherche, setRecherche] = useState("");
  const [filtreEmplacement, setFiltreEmplacement] = useState("");
  const [alertesUniquement, setAlertesUniquement] = useState(false);
  const [modalOuverte, setModalOuverte] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const [stocksResponse, articlesResponse, emplacementsResponse, resumeResponse] =
        await Promise.all([
          fetch(`${API_URL}/api/stocks`),
          fetch(`${API_URL}/api/articles`),
          fetch(`${API_URL}/api/emplacements?racines_uniquement=false`),
          fetch(`${API_URL}/api/stocks/resume`),
        ]);

      if (
        !stocksResponse.ok ||
        !articlesResponse.ok ||
        !emplacementsResponse.ok ||
        !resumeResponse.ok
      ) {
        throw new Error();
      }

      const [stocksData, articlesData, emplacementsData, resumeData] =
        await Promise.all([
          stocksResponse.json(),
          articlesResponse.json(),
          emplacementsResponse.json(),
          resumeResponse.json(),
        ]);

      setStocks(stocksData);
      setArticles(articlesData);
      setEmplacements(emplacementsData);
      setResume(resumeData);
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger le module Stock.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const stocksFiltres = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    return stocks.filter((stock) => {
      const correspondRecherche =
        !terme ||
        stock.article.reference.toLowerCase().includes(terme) ||
        stock.article.designation.toLowerCase().includes(terme) ||
        stock.emplacement.nom.toLowerCase().includes(terme) ||
        stock.emplacement.code.toLowerCase().includes(terme);

      const correspondEmplacement =
        !filtreEmplacement ||
        stock.emplacement_id === Number(filtreEmplacement);

      const correspondAlerte =
        !alertesUniquement ||
        Number(stock.quantite_disponible) <=
          Math.max(
            Number(stock.article.stock_minimum),
            Number(stock.article.seuil_alerte)
          );

      return correspondRecherche && correspondEmplacement && correspondAlerte;
    });
  }, [stocks, recherche, filtreEmplacement, alertesUniquement]);

  async function enregistrer(event: FormEvent) {
    event.preventDefault();

    try {
      const response = await fetch(`${API_URL}/api/stocks`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          article_id: Number(form.article_id),
          emplacement_id: Number(form.emplacement_id),
          quantite_physique: Number(form.quantite_physique),
          quantite_reservee: Number(form.quantite_reservee),
        }),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail ?? "Enregistrement impossible.");
      }

      setModalOuverte(false);
      setForm(initialForm);
      setToast({
        type: "success",
        message: "Le stock a été enregistré.",
      });
      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Enregistrement impossible.",
      });
    }
  }

  function modifier(stock: Stock) {
    setForm({
      article_id: String(stock.article_id),
      emplacement_id: String(stock.emplacement_id),
      quantite_physique: String(stock.quantite_physique),
      quantite_reservee: String(stock.quantite_reservee),
    });
    setModalOuverte(true);
  }

  return (
    <div>
      <div className="breadcrumb">Exploitation / Stocks</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Exploitation</span>
          <h1>Stocks</h1>
          <p>
            Consultez les quantités physiques, réservées et disponibles par
            emplacement.
          </p>
        </div>

        <Button variant="secondary" onClick={() => setModalOuverte(true)}>
          <Plus size={18} />
          Définir un stock
        </Button>
      </div>

      <section className="stock-metrics">
        <article className="stock-metric">
          <PackageCheck size={20} />
          <div>
            <span>Articles stockés</span>
            <strong>{resume.articles_stockes}</strong>
          </div>
        </article>
        <article className="stock-metric">
          <Warehouse size={20} />
          <div>
            <span>Lignes de stock</span>
            <strong>{resume.lignes_stock}</strong>
          </div>
        </article>
        <article className="stock-metric">
          <AlertTriangle size={20} />
          <div>
            <span>Alertes</span>
            <strong>{resume.alertes}</strong>
          </div>
        </article>
        <article className="stock-metric stock-metric-danger">
          <CircleGauge size={20} />
          <div>
            <span>Ruptures</span>
            <strong>{resume.ruptures}</strong>
          </div>
        </article>
      </section>

      <section className="content-card">
        <div className="stock-filters">
          <label className="search-field">
            <Search size={17} />
            <input
              type="search"
              placeholder="Rechercher un article ou un emplacement"
              value={recherche}
              onChange={(event) => setRecherche(event.target.value)}
            />
          </label>

          <select
            value={filtreEmplacement}
            onChange={(event) => setFiltreEmplacement(event.target.value)}
          >
            <option value="">Tous les emplacements</option>
            {emplacements.map((emplacement) => (
              <option key={emplacement.id} value={emplacement.id}>
                {emplacement.nom}
              </option>
            ))}
          </select>

          <label className="toggle-filter">
            <input
              type="checkbox"
              checked={alertesUniquement}
              onChange={(event) => setAlertesUniquement(event.target.checked)}
            />
            Alertes uniquement
          </label>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Article</th>
                <th>Emplacement</th>
                <th>Physique</th>
                <th>Réservé</th>
                <th>Disponible</th>
                <th>Mini</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {stocksFiltres.map((stock) => {
                const statut = statutStock(stock);

                return (
                  <tr
                    key={stock.id}
                    className="clickable-row"
                    onClick={() => modifier(stock)}
                  >
                    <td>
                      <div className="stock-article-cell">
                        <span className="reference-chip">
                          {stock.article.reference}
                        </span>
                        <strong>{stock.article.designation}</strong>
                      </div>
                    </td>
                    <td>
                      <strong>{stock.emplacement.nom}</strong>
                      <small className="table-subtext">
                        {stock.emplacement.code}
                      </small>
                    </td>
                    <td>
                      {Number(stock.quantite_physique).toLocaleString("fr-FR")}{" "}
                      {stock.article.unite}
                    </td>
                    <td>
                      {Number(stock.quantite_reservee).toLocaleString("fr-FR")}{" "}
                      {stock.article.unite}
                    </td>
                    <td>
                      <strong>
                        {Number(stock.quantite_disponible).toLocaleString("fr-FR")}{" "}
                        {stock.article.unite}
                      </strong>
                    </td>
                    <td>
                      {Number(stock.article.stock_minimum).toLocaleString("fr-FR")}{" "}
                      {stock.article.unite}
                    </td>
                    <td>
                      <Badge tone={statut.tone}>{statut.label}</Badge>
                    </td>
                  </tr>
                );
              })}

              {stocksFiltres.length === 0 && (
                <tr>
                  <td colSpan={7} className="empty-state">
                    <Boxes size={24} />
                    <strong>Aucune ligne de stock</strong>
                    <span>
                      Définissez le stock initial d’un article dans un
                      emplacement.
                    </span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {modalOuverte && (
        <div className="modal-backdrop" onMouseDown={() => setModalOuverte(false)}>
          <section
            className="modal-card"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">Stock initial / correction</span>
                <h2>Définir un stock</h2>
                <p>
                  Cette saisie directe sera remplacée par les mouvements
                  historisés dans le prochain lot.
                </p>
              </div>
            </div>

            <form onSubmit={enregistrer}>
              <div className="form-grid">
                <label className="field field-wide">
                  <span>Article *</span>
                  <select
                    required
                    value={form.article_id}
                    onChange={(event) =>
                      setForm({ ...form, article_id: event.target.value })
                    }
                  >
                    <option value="">Sélectionner</option>
                    {articles.map((article) => (
                      <option key={article.id} value={article.id}>
                        {article.reference} — {article.designation}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field field-wide">
                  <span>Emplacement *</span>
                  <select
                    required
                    value={form.emplacement_id}
                    onChange={(event) =>
                      setForm({ ...form, emplacement_id: event.target.value })
                    }
                  >
                    <option value="">Sélectionner</option>
                    {emplacements.map((emplacement) => (
                      <option key={emplacement.id} value={emplacement.id}>
                        {emplacement.nom} — {emplacement.code}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Quantité physique *</span>
                  <input
                    required
                    type="number"
                    min="0"
                    step="0.001"
                    value={form.quantite_physique}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        quantite_physique: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Quantité réservée</span>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={form.quantite_reservee}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        quantite_reservee: event.target.value,
                      })
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
                <Button type="submit">Enregistrer le stock</Button>
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
