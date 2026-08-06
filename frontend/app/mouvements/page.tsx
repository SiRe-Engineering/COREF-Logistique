"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  ArrowDownToLine,
  ArrowLeftRight,
  ArrowUpFromLine,
  History,
  Plus,
  RotateCcw,
  Search,
  SlidersHorizontal,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/components/auth/AuthProvider";
import { entetesAuthentifiees } from "@/lib/auth";
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

type Emplacement = {
  id: number;
  code: string;
  nom: string;
};

type Affaire = {
  id: number;
  reference: string;
  code_externe: string | null;
  nom: string;
  client: string | null;
  site: string | null;
  zone_intervention: string | null;
  charge_affaires: string | null;
  statut: string;
};

type Lot = {
  id: number;
  article_id: number;
  reference_interne: string;
  numero_lot_fournisseur: string;
  date_peremption: string;
};

type Mouvement = {
  id: number;
  reference: string;
  type: string;
  article_id: number;
  lot_id: number | null;
  emplacement_source_id: number | null;
  emplacement_destination_id: number | null;
  quantite: string;
  motif: string | null;
  commentaire: string | null;
  operateur: string | null;
  date_creation: string;
  article: Article;
  lot: Lot | null;
  affaire: Affaire | null;
  affaire_id: number | null;
  sortie_libre: boolean;
  zone_intervention: string | null;
  charge_affaires: string | null;
  vehicule: string | null;
  emplacement_source: Emplacement | null;
  emplacement_destination: Emplacement | null;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialForm = {
  type: "ENTREE",
  article_id: "",
  lot_id: "",
  affaire_id: "",
  sortie_libre: false,
  zone_intervention: "",
  charge_affaires: "",
  vehicule: "",
  emplacement_source_id: "",
  emplacement_destination_id: "",
  quantite: "",
  motif: "",
  commentaire: "",
  operateur: "Utilisateur local",
};

const types = [
  { value: "ENTREE", label: "Entrée" },
  { value: "SORTIE", label: "Sortie" },
  { value: "TRANSFERT", label: "Transfert" },
  { value: "RETOUR", label: "Retour" },
  { value: "AJUSTEMENT_POSITIF", label: "Ajustement +" },
  { value: "AJUSTEMENT_NEGATIF", label: "Ajustement −" },
];

function libelleType(type: string) {
  return types.find((element) => element.value === type)?.label ?? type;
}

function TypeIcon({ type }: { type: string }) {
  if (type === "ENTREE") return <ArrowDownToLine size={17} />;
  if (type === "SORTIE") return <ArrowUpFromLine size={17} />;
  if (type === "TRANSFERT") return <ArrowLeftRight size={17} />;
  if (type === "RETOUR") return <RotateCcw size={17} />;
  return <SlidersHorizontal size={17} />;
}

export default function MouvementsPage() {
  const { utilisateur } = useAuth();
  const adminTechnique =
    utilisateur?.role === "ADMINISTRATEUR_TECHNIQUE";
  const [mouvements, setMouvements] = useState<Mouvement[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [lots, setLots] = useState<Lot[]>([]);
  const [affaires, setAffaires] = useState<Affaire[]>([]);
  const [recherche, setRecherche] = useState("");
  const [filtreType, setFiltreType] = useState("");
  const [modalOuverte, setModalOuverte] = useState(false);
  const [enregistrement, setEnregistrement] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const [
        mouvementsResponse,
        articlesResponse,
        emplacementsResponse,
        lotsResponse,
        affairesResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/api/mouvements`),
        fetch(`${API_URL}/api/articles`),
        fetch(`${API_URL}/api/emplacements?racines_uniquement=false`),
        fetch(`${API_URL}/api/lots-beton`),
        fetch(`${API_URL}/api/affaires`),
      ]);

      if (
        !mouvementsResponse.ok ||
        !articlesResponse.ok ||
        !emplacementsResponse.ok ||
        !lotsResponse.ok ||
        !affairesResponse.ok
      ) {
        throw new Error();
      }

      const [
        mouvementsData,
        articlesData,
        emplacementsData,
        lotsData,
        affairesData,
      ] = await Promise.all([
        mouvementsResponse.json(),
        articlesResponse.json(),
        emplacementsResponse.json(),
        lotsResponse.json(),
        affairesResponse.json(),
      ]);

      setMouvements(mouvementsData);
      setArticles(articlesData);
      setEmplacements(emplacementsData);
      setLots(lotsData);
      setAffaires(affairesData);
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger les mouvements.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const articleSelectionne = articles.find(
    (article) => article.id === Number(form.article_id)
  );

  const articleEstBeton =
    articleSelectionne?.famille_relation?.code === "BET";

  const lotsArticle = lots
    .filter((lot) => lot.article_id === Number(form.article_id))
    .sort((a, b) =>
      a.date_peremption.localeCompare(b.date_peremption)
    );

  const mouvementsFiltres = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    return mouvements.filter((mouvement) => {
      const correspondRecherche =
        !terme ||
        mouvement.reference.toLowerCase().includes(terme) ||
        mouvement.article.reference.toLowerCase().includes(terme) ||
        mouvement.article.designation.toLowerCase().includes(terme) ||
        (mouvement.lot?.numero_lot_fournisseur ?? "")
          .toLowerCase()
          .includes(terme) ||
        (mouvement.motif ?? "").toLowerCase().includes(terme);

      const correspondType =
        !filtreType || mouvement.type === filtreType;

      return correspondRecherche && correspondType;
    });
  }, [mouvements, recherche, filtreType]);

  const typeSourceRequise = [
    "SORTIE",
    "TRANSFERT",
    "AJUSTEMENT_NEGATIF",
  ].includes(form.type);

  const typeDestinationRequise = [
    "ENTREE",
    "TRANSFERT",
    "RETOUR",
    "AJUSTEMENT_POSITIF",
  ].includes(form.type);

  async function enregistrer(event: FormEvent) {
    event.preventDefault();
    setEnregistrement(true);

    try {
      const response = await fetch(`${API_URL}/api/mouvements`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: form.type,
          article_id: Number(form.article_id),
          lot_id: form.lot_id ? Number(form.lot_id) : null,
          affaire_id: form.affaire_id ? Number(form.affaire_id) : null,
          sortie_libre: form.sortie_libre,
          zone_intervention: form.zone_intervention || null,
          charge_affaires: form.charge_affaires || null,
          vehicule: form.vehicule || null,
          emplacement_source_id: form.emplacement_source_id
            ? Number(form.emplacement_source_id)
            : null,
          emplacement_destination_id:
            form.emplacement_destination_id
              ? Number(form.emplacement_destination_id)
              : null,
          quantite: Number(form.quantite),
          motif: form.motif || null,
          commentaire: form.commentaire || null,
          operateur: form.operateur || null,
        }),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(
          typeof detail?.detail === "string"
            ? detail.detail
            : "Mouvement impossible."
        );
      }

      const mouvement: Mouvement = await response.json();

      setModalOuverte(false);
      setForm(initialForm);
      setToast({
        type: "success",
        message: `${mouvement.reference} enregistré avec succès.`,
      });
      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Mouvement impossible.",
      });
    } finally {
      setEnregistrement(false);
    }
  }


  async function supprimerMouvement(mouvement: Mouvement) {
    const motif = window.prompt(
      `Motif d’annulation de ${mouvement.reference} (obligatoire) :`
    );
    if (!motif?.trim()) return;

    if (
      !window.confirm(
        `Annuler l’écriture ${mouvement.reference} ?\n\n` +
          "Son effet sera automatiquement contre-passé dans le stock."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/mouvements/${mouvement.id}`,
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
            : "Annulation impossible."
        );
      }

      setToast({
        type: "success",
        message: `${mouvement.reference} annulé et contre-passé.`,
      });
      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Annulation impossible.",
      });
    }
  }

  return (
    <div>
      <div className="breadcrumb">Exploitation / Mouvements</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Traçabilité</span>
          <h1>Mouvements de stock</h1>
          <p>
            Enregistrez les entrées, sorties, transferts, retours et
            ajustements.
          </p>
        </div>

        <Button
          variant="secondary"
          onClick={() => setModalOuverte(true)}
        >
          <Plus size={18} />
          Nouveau mouvement
        </Button>
      </div>

      <section className={styles.summary}>
        <article>
          <History size={20} />
          <div>
            <span>Mouvements enregistrés</span>
            <strong>{mouvements.length}</strong>
          </div>
        </article>
        <article>
          <ArrowDownToLine size={20} />
          <div>
            <span>Entrées</span>
            <strong>
              {mouvements.filter((m) => m.type === "ENTREE").length}
            </strong>
          </div>
        </article>
        <article>
          <ArrowUpFromLine size={20} />
          <div>
            <span>Sorties</span>
            <strong>
              {mouvements.filter((m) => m.type === "SORTIE").length}
            </strong>
          </div>
        </article>
        <article>
          <ArrowLeftRight size={20} />
          <div>
            <span>Transferts</span>
            <strong>
              {mouvements.filter((m) => m.type === "TRANSFERT").length}
            </strong>
          </div>
        </article>
      </section>

      <section className="content-card">
        <div className={styles.filters}>
          <label className="search-field">
            <Search size={17} />
            <input
              type="search"
              placeholder="Référence, article, lot ou motif"
              value={recherche}
              onChange={(event) => setRecherche(event.target.value)}
            />
          </label>

          <select
            value={filtreType}
            onChange={(event) => setFiltreType(event.target.value)}
          >
            <option value="">Tous les types</option>
            {types.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Mouvement</th>
                <th>Date</th>
                <th>Type</th>
                <th>Article / lot</th>
                <th>Flux</th>
                <th>Quantité</th>
                <th>Affaire</th>
                <th>Motif</th>
                {adminTechnique && <th aria-label="Actions" />}
              </tr>
            </thead>
            <tbody>
              {mouvementsFiltres.map((mouvement) => (
                <tr key={mouvement.id}>
                  <td>
                    <span className="reference-chip">
                      {mouvement.reference}
                    </span>
                  </td>
                  <td>
                    {new Intl.DateTimeFormat("fr-FR", {
                      dateStyle: "short",
                      timeStyle: "short",
                    }).format(new Date(mouvement.date_creation))}
                  </td>
                  <td>
                    <span
                      className={`${styles.typeBadge} ${
                        styles[
                          `type${mouvement.type
                            .toLowerCase()
                            .replaceAll("_", "")}`
                        ]
                      }`}
                    >
                      <TypeIcon type={mouvement.type} />
                      {libelleType(mouvement.type)}
                    </span>
                  </td>
                  <td>
                    <div className={styles.articleCell}>
                      <strong>{mouvement.article.designation}</strong>
                      <small>{mouvement.article.reference}</small>
                      {mouvement.lot && (
                        <small>
                          Lot {mouvement.lot.numero_lot_fournisseur}
                        </small>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className={styles.flow}>
                      <span>
                        {mouvement.emplacement_source?.nom ?? "Extérieur"}
                      </span>
                      <span>→</span>
                      <span>
                        {mouvement.emplacement_destination?.nom ??
                          "Extérieur"}
                      </span>
                    </div>
                  </td>
                  <td>
                    <strong>
                      {Number(mouvement.quantite).toLocaleString("fr-FR")}{" "}
                      {mouvement.article.unite}
                    </strong>
                  </td>
                  <td>
                    {mouvement.affaire
                      ? mouvement.affaire.code_externe ||
                        mouvement.affaire.reference
                      : mouvement.sortie_libre
                        ? "Sortie libre"
                        : "—"}
                  </td>
                  <td>{mouvement.motif ?? "—"}</td>
                  {adminTechnique && (
                    <td>
                      <button
                        type="button"
                        className="icon-button danger"
                        onClick={() => supprimerMouvement(mouvement)}
                        title="Annuler cette écriture"
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  )}
                </tr>
              ))}

              {mouvementsFiltres.length === 0 && (
                <tr>
                  <td colSpan={adminTechnique ? 9 : 8} className="empty-state">
                    <History size={24} />
                    <strong>Aucun mouvement</strong>
                    <span>
                      Enregistrez une entrée, une sortie ou un transfert.
                    </span>
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
                <span className="eyebrow">Nouveau flux</span>
                <h2>Enregistrer un mouvement</h2>
                <p>
                  Pour un béton, le choix du lot est obligatoire.
                </p>
              </div>
            </div>

            <form onSubmit={enregistrer}>
              <div className="form-grid">
                <label className="field">
                  <span>Type *</span>
                  <select
                    required
                    value={form.type}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        type: event.target.value,
                        emplacement_source_id: "",
                        emplacement_destination_id: "",
                      })
                    }
                  >
                    {types.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Quantité *</span>
                  <input
                    required
                    type="number"
                    min="0.001"
                    step="0.001"
                    value={form.quantite}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        quantite: event.target.value,
                      })
                    }
                  />
                </label>

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
  affaire_id: "",
  sortie_libre: false,
  zone_intervention: "",
  charge_affaires: "",
  vehicule: "",
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
                          {lot.numero_lot_fournisseur} — échéance{" "}
                          {new Intl.DateTimeFormat("fr-FR").format(
                            new Date(`${lot.date_peremption}T00:00:00`)
                          )}
                        </option>
                      ))}
                    </select>
                    <small className="muted-text">
                      Les lots sont proposés par date de péremption
                      croissante (FEFO).
                    </small>
                  </label>
                )}


                {form.type === "SORTIE" && (
                  <>
                    <label className="field field-wide">
                      <span>Affaire chantier / atelier</span>
                      <select
                        value={form.affaire_id}
                        disabled={form.sortie_libre}
                        onChange={(event) => {
                          const affaire = affaires.find(
                            (element) =>
                              element.id === Number(event.target.value)
                          );
                          setForm({
                            ...form,
                            affaire_id: event.target.value,
                            charge_affaires:
                              affaire?.charge_affaires ?? "",
                            zone_intervention:
                              affaire?.zone_intervention ?? "",
                          });
                        }}
                      >
                        <option value="">Sélectionner</option>
                        {affaires
                          .filter(
                            (affaire) =>
                              !["TERMINEE", "ANNULEE"].includes(
                                affaire.statut
                              )
                          )
                          .map((affaire) => (
                            <option key={affaire.id} value={affaire.id}>
                              {affaire.code_externe || affaire.reference} —{" "}
                              {affaire.nom}
                            </option>
                          ))}
                      </select>
                    </label>

                    <label className="field field-wide">
                      <span className="toggle-filter">
                        <input
                          type="checkbox"
                          checked={form.sortie_libre}
                          onChange={(event) =>
                            setForm({
                              ...form,
                              sortie_libre: event.target.checked,
                              affaire_id: event.target.checked
                                ? ""
                                : form.affaire_id,
                            })
                          }
                        />
                        Sortie libre sans affaire
                      </span>
                    </label>

                    <label className="field">
                      <span>Chargé d’affaires</span>
                      <input
                        maxLength={150}
                        value={form.charge_affaires}
                        onChange={(event) =>
                          setForm({
                            ...form,
                            charge_affaires: event.target.value,
                          })
                        }
                      />
                    </label>

                    <label className="field">
                      <span>Zone d’intervention</span>
                      <input
                        maxLength={180}
                        value={form.zone_intervention}
                        onChange={(event) =>
                          setForm({
                            ...form,
                            zone_intervention: event.target.value,
                          })
                        }
                      />
                    </label>

                    <label className="field field-wide">
                      <span>Véhicule</span>
                      <input
                        maxLength={120}
                        placeholder="Ex. Camion 3, Renault Master..."
                        value={form.vehicule}
                        onChange={(event) =>
                          setForm({
                            ...form,
                            vehicule: event.target.value,
                          })
                        }
                      />
                    </label>
                  </>
                )}

                {typeSourceRequise && (
                  <label className="field">
                    <span>Emplacement source *</span>
                    <select
                      required
                      value={form.emplacement_source_id}
                      onChange={(event) =>
                        setForm({
                          ...form,
                          emplacement_source_id: event.target.value,
                        })
                      }
                    >
                      <option value="">Sélectionner</option>
                      {emplacements.map((emplacement) => (
                        <option
                          key={emplacement.id}
                          value={emplacement.id}
                        >
                          {emplacement.nom} — {emplacement.code}
                        </option>
                      ))}
                    </select>
                  </label>
                )}

                {typeDestinationRequise && (
                  <label
                    className={`field ${
                      !typeSourceRequise ? "field-wide" : ""
                    }`}
                  >
                    <span>Emplacement destination *</span>
                    <select
                      required
                      value={form.emplacement_destination_id}
                      onChange={(event) =>
                        setForm({
                          ...form,
                          emplacement_destination_id:
                            event.target.value,
                        })
                      }
                    >
                      <option value="">Sélectionner</option>
                      {emplacements.map((emplacement) => (
                        <option
                          key={emplacement.id}
                          value={emplacement.id}
                        >
                          {emplacement.nom} — {emplacement.code}
                        </option>
                      ))}
                    </select>
                  </label>
                )}

                <label className="field field-wide">
                  <span>Motif</span>
                  <input
                    maxLength={150}
                    placeholder="Ex. Réception fournisseur, chantier..."
                    value={form.motif}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        motif: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field field-wide">
                  <span>Commentaire</span>
                  <textarea
                    className={styles.textarea}
                    rows={3}
                    value={form.commentaire}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        commentaire: event.target.value,
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
                  disabled={enregistrement}
                >
                  Annuler
                </Button>
                <Button type="submit" disabled={enregistrement}>
                  {enregistrement
                    ? "Enregistrement…"
                    : "Valider le mouvement"}
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
