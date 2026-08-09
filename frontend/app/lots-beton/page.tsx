"use client";

import { apiFetch } from "@/lib/api";

import Link from "next/link";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  CalendarClock,
  FileCheck2,
  FileText,
  FlaskConical,
  Plus,
  Printer,
  Search,
  TriangleAlert,
  Trash2,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { useAuth } from "@/components/auth/AuthProvider";
import { entetesAuthentifiees } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";
import styles from "./page.module.css";

type Article = {
  id: number;
  reference: string;
  designation: string;
  unite: string;
  famille_relation: {
    id: number;
    code: string;
    nom: string;
  } | null;
};

type StockLot = {
  id: number;
  emplacement_id: number;
  quantite_physique: string;
  quantite_reservee: string;
  quantite_disponible: string;
  emplacement: {
    id: number;
    code: string;
    nom: string;
  };
};

type Lot = {
  id: number;
  reference_interne: string;
  article_id: number;
  numero_lot_fournisseur: string;
  date_fabrication: string;
  date_peremption: string;
  fournisseur: string | null;
  certificat_reference: string | null;
  fds_reference: string | null;
  commentaire: string | null;
  actif: boolean;
  article: Article;
  stocks: StockLot[];
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialForm = {
  article_id: "",
  numero_lot_fournisseur: "",
  date_fabrication: "",
  date_peremption: "",
  fournisseur: "",
  certificat_reference: "",
  fds_reference: "",
  commentaire: "",
};

function joursAvantPeremption(datePeremption: string) {
  const aujourdHui = new Date();
  aujourdHui.setHours(0, 0, 0, 0);

  const date = new Date(`${datePeremption}T00:00:00`);
  return Math.ceil(
    (date.getTime() - aujourdHui.getTime()) / 86_400_000
  );
}

function statutPeremption(datePeremption: string) {
  const jours = joursAvantPeremption(datePeremption);

  if (jours < 0) {
    return { label: "Périmé", tone: "beton" as const };
  }
  if (jours <= 30) {
    return { label: `${jours} j`, tone: "warning" as const };
  }
  return { label: "Valide", tone: "success" as const };
}

export default function LotsBetonPage() {
  const { utilisateur } = useAuth();
  const adminTechnique =
    utilisateur?.role === "ADMINISTRATEUR_TECHNIQUE";
  const [lots, setLots] = useState<Lot[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [recherche, setRecherche] = useState("");
  const [filtreArticle, setFiltreArticle] = useState("");
  const [modalOuverte, setModalOuverte] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const [lotsResponse, articlesResponse] = await Promise.all([
        apiFetch(`${API_URL}/api/lots-beton`),
        apiFetch(`${API_URL}/api/articles`),
      ]);

      if (!lotsResponse.ok || !articlesResponse.ok) {
        throw new Error();
      }

      const [lotsData, articlesData] = await Promise.all([
        lotsResponse.json(),
        articlesResponse.json(),
      ]);

      setLots(lotsData);
      setArticles(
        articlesData.filter(
          (article: Article) =>
            article.famille_relation?.code === "BET"
        )
      );
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger les lots béton.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const lotsFiltres = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    return lots.filter((lot) => {
      const correspondRecherche =
        !terme ||
        lot.reference_interne.toLowerCase().includes(terme) ||
        lot.numero_lot_fournisseur.toLowerCase().includes(terme) ||
        lot.article.reference.toLowerCase().includes(terme) ||
        lot.article.designation.toLowerCase().includes(terme) ||
        (lot.fournisseur ?? "").toLowerCase().includes(terme);

      const correspondArticle =
        !filtreArticle || lot.article_id === Number(filtreArticle);

      return correspondRecherche && correspondArticle;
    });
  }, [lots, recherche, filtreArticle]);

  const lotsProchesPeremption = lots.filter(
    (lot) => joursAvantPeremption(lot.date_peremption) <= 30
  ).length;

  async function creer(event: FormEvent) {
    event.preventDefault();

    try {
      const response = await apiFetch(`${API_URL}/api/lots-beton`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          article_id: Number(form.article_id),
          numero_lot_fournisseur: form.numero_lot_fournisseur,
          date_fabrication: form.date_fabrication,
          date_peremption: form.date_peremption,
          fournisseur: form.fournisseur || null,
          certificat_reference:
            form.certificat_reference || null,
          fds_reference: form.fds_reference || null,
          commentaire: form.commentaire || null,
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

      const lot: Lot = await response.json();

      setModalOuverte(false);
      setForm(initialForm);
      setToast({
        type: "success",
        message: `${lot.reference_interne} créé.`,
      });
      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Création impossible.",
      });
    }
  }


  async function supprimerLot(lot: Lot) {
    const motif = window.prompt(
      `Motif de suppression de ${lot.reference_interne} (obligatoire) :`
    );
    if (!motif?.trim()) return;

    if (
      !window.confirm(
        `Supprimer le lot ${lot.reference_interne} ?\n\n` +
          "Cette action l’archive définitivement de l’interface."
      )
    ) {
      return;
    }

    try {
      const response = await apiFetch(
        `${API_URL}/api/lots-beton/${lot.id}`,
        {
          method: "DELETE",
          headers: entetesAuthentifiees({
            "Content-Type": "application/json",
          }),
          body: JSON.stringify({ motif: motif.trim() }),
        }
      );

      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : "Suppression impossible."
        );
      }

      setToast({
        type: "success",
        message: `${lot.reference_interne} supprimé.`,
      });
      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Suppression impossible.",
      });
    }
  }

  return (
    <div>
      <div className="breadcrumb">Qualité / Lots béton</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Traçabilité renforcée</span>
          <h1>Lots béton</h1>
          <p>
            Suivez la fabrication, la péremption, les documents et le
            stock de chaque lot.
          </p>
        </div>

        <div className={styles.headerActions}><Link href="/documents-fournisseurs">Documents fournisseurs</Link><Button
          variant="secondary"
          onClick={() => setModalOuverte(true)}
        >
          <Plus size={18} />
          Nouveau lot
        </Button></div>
      </div>

      <section className={styles.summary}>
        <article>
          <FlaskConical size={20} />
          <div>
            <span>Lots actifs</span>
            <strong>{lots.length}</strong>
          </div>
        </article>
        <article>
          <CalendarClock size={20} />
          <div>
            <span>Échéance sous 30 jours</span>
            <strong>{lotsProchesPeremption}</strong>
          </div>
        </article>
        <article>
          <FileCheck2 size={20} />
          <div>
            <span>Certificats renseignés</span>
            <strong>
              {lots.filter((lot) => lot.certificat_reference).length}
            </strong>
          </div>
        </article>
        <article>
          <FileText size={20} />
          <div>
            <span>FDS renseignées</span>
            <strong>{lots.filter((lot) => lot.fds_reference).length}</strong>
          </div>
        </article>
      </section>

      <section className="content-card">
        <div className={styles.filters}>
          <label className="search-field">
            <Search size={17} />
            <input
              type="search"
              placeholder="Lot, article ou fournisseur"
              value={recherche}
              onChange={(event) => setRecherche(event.target.value)}
            />
          </label>

          <select
            value={filtreArticle}
            onChange={(event) => setFiltreArticle(event.target.value)}
          >
            <option value="">Tous les bétons</option>
            {articles.map((article) => (
              <option key={article.id} value={article.id}>
                {article.reference} — {article.designation}
              </option>
            ))}
          </select>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Lot</th>
                <th>Article</th>
                <th>Fournisseur</th>
                <th>Fabrication</th>
                <th>Péremption</th>
                <th>Stock disponible</th>
                <th>Documents</th>
                <th>Statut</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {lotsFiltres.map((lot) => {
                const statut = statutPeremption(lot.date_peremption);
                const disponible = lot.stocks.reduce(
                  (total, stock) =>
                    total + Number(stock.quantite_disponible),
                  0
                );

                return (
                  <tr key={lot.id}>
                    <td>
                      <div className={styles.lotCell}>
                        <span className="reference-chip">
                          {lot.reference_interne}
                        </span>
                        <strong>{lot.numero_lot_fournisseur}</strong>
                      </div>
                    </td>
                    <td>
                      <strong>{lot.article.designation}</strong>
                      <small className="table-subtext">
                        {lot.article.reference}
                      </small>
                    </td>
                    <td>{lot.fournisseur ?? "—"}</td>
                    <td>
                      {new Intl.DateTimeFormat("fr-FR").format(
                        new Date(`${lot.date_fabrication}T00:00:00`)
                      )}
                    </td>
                    <td>
                      {new Intl.DateTimeFormat("fr-FR").format(
                        new Date(`${lot.date_peremption}T00:00:00`)
                      )}
                    </td>
                    <td>
                      <strong>
                        {disponible.toLocaleString("fr-FR")}{" "}
                        {lot.article.unite}
                      </strong>
                    </td>
                    <td>
                      <div className={styles.documents}>
                        <span
                          className={
                            lot.certificat_reference
                              ? styles.documentOk
                              : styles.documentMissing
                          }
                        >
                          Certificat
                        </span>
                        <span
                          className={
                            lot.fds_reference
                              ? styles.documentOk
                              : styles.documentMissing
                          }
                        >
                          FDS
                        </span>
                      </div>
                    </td>
                    <td>
                      <Badge tone={statut.tone}>{statut.label}</Badge>
                    </td>
                    <td>
                      <div className={styles.documents}>
                        <button
                          type="button"
                          className="icon-button"
                          onClick={() =>
                            window.open(
                              `/lots-beton/${lot.id}/etiquette`,
                              "_blank",
                              "noopener,noreferrer"
                            )
                          }
                          title="Imprimer l’étiquette QR"
                        >
                          <Printer size={15} />
                        </button>
                        {adminTechnique && (
                          <button
                            type="button"
                            className="icon-button danger"
                            onClick={() => supprimerLot(lot)}
                            title="Supprimer ce lot"
                          >
                            <Trash2 size={15} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}

              {lotsFiltres.length === 0 && (
                <tr>
                  <td colSpan={9} className="empty-state">
                    <TriangleAlert size={24} />
                    <strong>Aucun lot béton</strong>
                    <span>Créez le premier lot fournisseur.</span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

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
                <span className="eyebrow">Traçabilité fournisseur</span>
                <h2>Créer un lot béton</h2>
                <p>
                  Créez le lot puis déposez le certificat fournisseur et la FDS depuis le module Documents fournisseurs.
                </p>
              </div>
            </div>

            <form onSubmit={creer}>
              <div className="form-grid">
                <label className="field field-wide">
                  <span>Article béton *</span>
                  <select
                    required
                    value={form.article_id}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        article_id: event.target.value,
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

                <label className="field field-wide">
                  <span>Numéro de lot fournisseur *</span>
                  <input
                    required
                    maxLength={120}
                    value={form.numero_lot_fournisseur}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        numero_lot_fournisseur:
                          event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Date de fabrication *</span>
                  <input
                    required
                    type="date"
                    value={form.date_fabrication}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        date_fabrication: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Date de péremption *</span>
                  <input
                    required
                    type="date"
                    value={form.date_peremption}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        date_peremption: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field field-wide">
                  <span>Fournisseur</span>
                  <input
                    maxLength={180}
                    value={form.fournisseur}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        fournisseur: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Référence certificat</span>
                  <input
                    maxLength={255}
                    placeholder="Ex. CERT-2026-1458"
                    value={form.certificat_reference}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        certificat_reference:
                          event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Référence FDS</span>
                  <input
                    maxLength={255}
                    placeholder="Ex. FDS-LB85-REV4"
                    value={form.fds_reference}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        fds_reference: event.target.value,
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
                <Button type="submit">Créer le lot</Button>
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
