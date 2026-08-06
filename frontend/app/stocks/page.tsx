"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CircleGauge,
  PackageCheck,
  Plus,
  RotateCcw,
  Search,
  Warehouse,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { useAuth } from "@/components/auth/AuthProvider";
import { entetesAuthentifiees } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Toast } from "@/components/ui/Toast";
import styles from "./page.module.css";

type Article = {
  id: number;
  reference: string;
  designation: string;
  unite: string;
  stock_minimum: string;
  stock_maximum: string;
  seuil_alerte: string;
  famille_relation: { code: string } | null;
};

type Lot = {
  id: number;
  article_id: number;
  numero_lot_fournisseur: string;
  date_peremption: string;
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

type Reservation = {
  id: number;
  reference: string;
  quantite: string;
  reserve_pour: string;
  reserve_par: string | null;
  motif: string | null;
  date_creation: string;
  lot: { numero_lot_fournisseur: string } | null;
  preparation: { reference: string; nom: string } | null;
};

type Resume = {
  lignes_stock: number;
  articles_stockes: number;
  ruptures: number;
  alertes: number;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialForm = {
  article_id: "",
  lot_id: "",
  emplacement_id: "",
  quantite_physique: "0",
};

function statutStock(stock: Stock) {
  const disponible = Number(stock.quantite_disponible);
  const seuil = Math.max(
    Number(stock.article.stock_minimum),
    Number(stock.article.seuil_alerte)
  );

  if (disponible <= 0) {
    return { label: "Rupture", tone: "beton" as const };
  }
  if (disponible <= seuil) {
    return { label: "Alerte", tone: "warning" as const };
  }
  return { label: "Disponible", tone: "success" as const };
}

export default function StocksPage() {
  const { utilisateur } = useAuth();
  const adminTechnique =
    utilisateur?.role === "ADMINISTRATEUR_TECHNIQUE";
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [lots, setLots] = useState<Lot[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [selection, setSelection] = useState<Stock | null>(null);
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
      const responses = await Promise.all([
        fetch(`${API_URL}/api/stocks`),
        fetch(`${API_URL}/api/articles`),
        fetch(`${API_URL}/api/emplacements?racines_uniquement=false`),
        fetch(`${API_URL}/api/stocks/resume`),
        fetch(`${API_URL}/api/lots-beton`),
      ]);

      if (responses.some((response) => !response.ok)) {
        throw new Error();
      }

      const [
        stocksData,
        articlesData,
        emplacementsData,
        resumeData,
        lotsData,
      ] = await Promise.all(
        responses.map((response) => response.json())
      );

      setStocks(stocksData);
      setArticles(articlesData);
      setEmplacements(emplacementsData);
      setResume(resumeData);
      setLots(lotsData);
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

  async function ouvrirStock(stock: Stock) {
    setSelection(stock);
    const response = await fetch(
      `${API_URL}/api/reservations?article_id=${stock.article_id}` +
        `&emplacement_id=${stock.emplacement_id}`
    );
    setReservations(response.ok ? await response.json() : []);
  }

  const articleSelectionne = articles.find(
    (article) => article.id === Number(form.article_id)
  );

  const articleEstBeton =
    articleSelectionne?.famille_relation?.code === "BET";

  const lotsArticle = lots.filter(
    (lot) => lot.article_id === Number(form.article_id)
  );

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

    if (articleEstBeton && !form.lot_id) {
      setToast({
        type: "error",
        message: "Un lot est obligatoire pour un stock béton.",
      });
      return;
    }

    const quantitePhysique = Number(
      form.quantite_physique.replace(",", ".")
    );

    if (!Number.isFinite(quantitePhysique) || quantitePhysique < 0) {
      setToast({
        type: "error",
        message: "La quantité physique est invalide.",
      });
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/stocks`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          article_id: Number(form.article_id),
          lot_id: form.lot_id ? Number(form.lot_id) : null,
          emplacement_id: Number(form.emplacement_id),
          quantite_physique: quantitePhysique,
        }),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(
          typeof detail?.detail === "string"
            ? detail.detail
            : "Enregistrement impossible."
        );
      }

      setModalOuverte(false);
      setForm(initialForm);
      setToast({
        type: "success",
        message: articleEstBeton
          ? "Le stock physique du lot a été enregistré."
          : "La quantité physique a été enregistrée.",
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


  async function remettreAZero(stock: Stock) {
    if (!adminTechnique) return;

    const confirmation = window.confirm(
      `Remettre entièrement à zéro le stock ${stock.article.reference} ` +
        `à ${stock.emplacement.nom} ?\n\n` +
        "Cette opération mettra à zéro :\n" +
        "• le stock physique article ;\n" +
        "• le stock réservé article ;\n" +
        "• tous les stocks de lots associés ;\n" +
        "• toutes les réservations actives sur cet article et cet emplacement."
    );

    if (!confirmation) return;

    try {
      const response = await fetch(
        `${API_URL}/api/stocks/${stock.id}/remise-a-zero`,
        {
          method: "POST",
          headers: entetesAuthentifiees(),
        }
      );

      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : "Remise à zéro impossible."
        );
      }

      setToast({
        type: "success",
        message:
          "Stock article, stocks de lots et réservations remis à zéro.",
      });

      if (selection?.id === stock.id) {
        setReservations([]);
      }

      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Remise à zéro impossible.",
      });
    }
  }

  return (
    <div>
      <div className="breadcrumb">Exploitation / Stocks</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Exploitation</span>
          <h1>Stocks</h1>
          <p>
            Les réservations sont calculées depuis les besoins identifiés.
          </p>
        </div>

        <Button
          variant="secondary"
          onClick={() => {
            setForm(initialForm);
            setModalOuverte(true);
          }}
        >
          <Plus size={18} />
          Définir un stock physique
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
        <div className="stock-toolbar">
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
            onChange={(event) =>
              setFiltreEmplacement(event.target.value)
            }
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
              onChange={(event) =>
                setAlertesUniquement(event.target.checked)
              }
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
                {adminTechnique && <th aria-label="Actions" />}
              </tr>
            </thead>
            <tbody>
              {stocksFiltres.map((stock) => {
                const statut = statutStock(stock);
                return (
                  <tr
                    key={stock.id}
                    className="clickable-row"
                    onClick={() => ouvrirStock(stock)}
                  >
                    <td>
                      <span className="reference-chip">
                        {stock.article.reference}
                      </span>
                      <strong className="table-title">
                        {stock.article.designation}
                      </strong>
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
                      <strong>
                        {Number(stock.quantite_reservee).toLocaleString("fr-FR")}{" "}
                        {stock.article.unite}
                      </strong>
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
                    {adminTechnique && (
                      <td>
                        <button
                          type="button"
                          className="icon-button"
                          title="Remettre ce stock à zéro"
                          onClick={(event) => {
                            event.stopPropagation();
                            remettreAZero(stock);
                          }}
                        >
                          <RotateCcw size={15} />
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <Drawer
        open={selection !== null}
        title={selection?.article.reference ?? ""}
        onClose={() => {
          setSelection(null);
          setReservations([]);
        }}
      >
        {selection && (
          <div>
            <h3>{selection.article.designation}</h3>
            <p className="muted-text">{selection.emplacement.nom}</p>

            <div className={styles.stockDetail}>
              <div>
                <span>Physique</span>
                <strong>{selection.quantite_physique}</strong>
              </div>
              <div>
                <span>Réservé</span>
                <strong>{selection.quantite_reservee}</strong>
              </div>
              <div>
                <span>Disponible</span>
                <strong>{selection.quantite_disponible}</strong>
              </div>
            </div>

            <section className="drawer-section">
              <h4>Détail des réservations</h4>
              <div className={styles.reservations}>
                {reservations.map((reservation) => (
                  <article key={reservation.id}>
                    <div>
                      <strong>{reservation.reserve_pour}</strong>
                      <span>{reservation.reference}</span>
                    </div>
                    <strong>
                      {Number(reservation.quantite).toLocaleString("fr-FR")}{" "}
                      {selection.article.unite}
                    </strong>
                    <small>
                      Demandé par {reservation.reserve_par ?? "—"}
                      {reservation.lot
                        ? ` · Lot ${reservation.lot.numero_lot_fournisseur}`
                        : ""}
                    </small>
                  </article>
                ))}

                {reservations.length === 0 && (
                  <p className="muted-text">Aucune réservation active.</p>
                )}
              </div>
            </section>
          </div>
        )}
      </Drawer>

      {modalOuverte && (
        <div
          className="modal-backdrop"
          onMouseDown={() => setModalOuverte(false)}
        >
          <section
            className="modal-card"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">Stock physique</span>
                <h2>Définir une quantité physique</h2>
                <p>
                  Pour un béton, le lot est obligatoire. La quantité
                  réservée reste gérée automatiquement.
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
                      setForm({
                        ...form,
                        article_id: event.target.value,
                        lot_id: "",
                      })
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

                {articleEstBeton && (
                  <label className="field field-wide">
                    <span>Lot béton *</span>
                    <select
                      required
                      value={form.lot_id}
                      onChange={(event) =>
                        setForm({
                          ...form,
                          lot_id: event.target.value,
                        })
                      }
                    >
                      <option value="">Sélectionner</option>
                      {lotsArticle.map((lot) => (
                        <option key={lot.id} value={lot.id}>
                          {lot.numero_lot_fournisseur}
                        </option>
                      ))}
                    </select>
                  </label>
                )}

                <label className="field field-wide">
                  <span>Emplacement *</span>
                  <select
                    required
                    value={form.emplacement_id}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        emplacement_id: event.target.value,
                      })
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

                <label className="field field-wide">
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
              </div>

              <div className="modal-actions">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setModalOuverte(false)}
                >
                  Annuler
                </Button>
                <Button type="submit">Enregistrer</Button>
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
