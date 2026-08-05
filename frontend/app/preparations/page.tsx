"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  Pencil,
  Play,
  Plus,
  Search,
  Send,
  Trash2,
  XCircle,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Toast } from "@/components/ui/Toast";
import styles from "./page.module.css";

type Affaire = {
  id: number;
  reference: string;
  code_externe: string | null;
  nom: string;
  client: string | null;
  site: string | null;
  zone_intervention: string | null;
  charge_affaires: string | null;
  date_debut: string | null;
  date_fin_prevue: string | null;
  statut: string;
};

type Article = {
  id: number;
  reference: string;
  designation: string;
  unite: string;
  famille_relation: { code: string } | null;
};

type Emplacement = {
  id: number;
  code: string;
  nom: string;
};

type Lot = {
  id: number;
  article_id: number;
  numero_lot_fournisseur: string;
  date_peremption: string;
};

type Ligne = {
  id: number;
  article_id: number;
  lot_id: number | null;
  emplacement_source_id: number | null;
  quantite_demandee: string;
  quantite_preparee: string;
  statut: string;
  commentaire: string | null;
  article: Article;
  lot: Lot | null;
  emplacement_source: Emplacement | null;
};

type Preparation = {
  id: number;
  reference: string;
  affaire_id: number;
  nom: string;
  statut: string;
  date_besoin: string | null;
  demandeur: string | null;
  preparateur: string | null;
  vehicule: string | null;
  commentaire: string | null;
  affaire: Affaire;
  lignes: Ligne[];
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const formulaireVide = {
  affaire_id: "",
  nom: "",
  date_besoin: "",
  demandeur: "",
  preparateur: "",
  vehicule: "",
  commentaire: "",
};

const ligneVide = {
  article_id: "",
  lot_id: "",
  emplacement_source_id: "",
  quantite_demandee: "",
  commentaire: "",
};


function statutPreparation(statut: string) {
  if (statut === "BROUILLON") {
    return { label: "Brouillon", tone: "warning" as const };
  }
  if (statut === "VALIDEE") {
    return { label: "Validée", tone: "isolants" as const };
  }
  if (statut === "EN_PREPARATION") {
    return { label: "En préparation", tone: "warning" as const };
  }
  if (statut === "PRETE") {
    return { label: "Prête", tone: "success" as const };
  }
  return { label: "Expédiée", tone: "neutral" as const };
}

function formaterDate(date: string | null) {
  if (!date) return "—";
  return new Intl.DateTimeFormat("fr-FR").format(
    new Date(`${date}T00:00:00`)
  );
}

function progression(preparation: Preparation) {
  if (preparation.lignes.length === 0) return 0;

  const demande = preparation.lignes.reduce(
    (total, ligne) => total + Number(ligne.quantite_demandee),
    0
  );
  const prepare = preparation.lignes.reduce(
    (total, ligne) =>
      total +
      Math.min(
        Number(ligne.quantite_preparee),
        Number(ligne.quantite_demandee)
      ),
    0
  );

  return demande > 0 ? Math.round((prepare / demande) * 100) : 0;
}

export default function PreparationsPage() {
  const [preparations, setPreparations] = useState<Preparation[]>([]);
  const [affaires, setAffaires] = useState<Affaire[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [lots, setLots] = useState<Lot[]>([]);
  const [selection, setSelection] = useState<Preparation | null>(null);
  const [recherche, setRecherche] = useState("");
  const [filtreStatut, setFiltreStatut] = useState("");
  const [modalOuverte, setModalOuverte] = useState(false);
  const [editionEntete, setEditionEntete] = useState(false);
  const [ligneEditee, setLigneEditee] = useState<Ligne | null>(null);
  const [form, setForm] = useState(formulaireVide);
  const [ligneForm, setLigneForm] = useState(ligneVide);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const responses = await Promise.all([
        fetch(`${API_URL}/api/preparations`),
        fetch(`${API_URL}/api/affaires`),
        fetch(`${API_URL}/api/articles`),
        fetch(`${API_URL}/api/emplacements?racines_uniquement=false`),
        fetch(`${API_URL}/api/lots-beton`),
      ]);

      if (responses.some((response) => !response.ok)) throw new Error();

      const data = await Promise.all(
        responses.map((response) => response.json())
      );

      setPreparations(data[0]);
      setAffaires(data[1]);
      setArticles(data[2]);
      setEmplacements(data[3]);
      setLots(data[4]);
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger les préparations.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const preparationsFiltrees = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    return preparations.filter((preparation) => {
      const correspondRecherche =
        !terme ||
        preparation.reference.toLowerCase().includes(terme) ||
        preparation.nom.toLowerCase().includes(terme) ||
        preparation.affaire.nom.toLowerCase().includes(terme) ||
        (preparation.affaire.code_externe ?? "")
          .toLowerCase()
          .includes(terme) ||
        (preparation.affaire.client ?? "")
          .toLowerCase()
          .includes(terme) ||
        (preparation.affaire.site ?? "")
          .toLowerCase()
          .includes(terme) ||
        (preparation.demandeur ?? "")
          .toLowerCase()
          .includes(terme) ||
        (preparation.preparateur ?? "")
          .toLowerCase()
          .includes(terme);

      const correspondStatut =
        !filtreStatut || preparation.statut === filtreStatut;

      return correspondRecherche && correspondStatut;
    });
  }, [preparations, recherche, filtreStatut]);

  const editable =
    selection !== null &&
    ["BROUILLON", "VALIDEE", "EN_PREPARATION"].includes(
      selection.statut
    );

  const articleSelectionne = articles.find(
    (article) => article.id === Number(ligneForm.article_id)
  );
  const articleEstBeton =
    articleSelectionne?.famille_relation?.code === "BET";
  const lotsArticle = lots.filter(
    (lot) => lot.article_id === Number(ligneForm.article_id)
  );

  function ouvrirPreparation(preparation: Preparation) {
    setSelection(preparation);
    setForm({
      affaire_id: String(preparation.affaire_id),
      nom: preparation.nom,
      date_besoin: preparation.date_besoin ?? "",
      demandeur: preparation.demandeur ?? "",
      preparateur: preparation.preparateur ?? "",
      vehicule: preparation.vehicule ?? "",
      commentaire: preparation.commentaire ?? "",
    });
    setEditionEntete(false);
    setLigneEditee(null);
    setLigneForm(ligneVide);
  }

  async function actualiserSelection(preparation: Preparation) {
    setSelection(preparation);
    setPreparations((actuelles) =>
      actuelles.map((element) =>
        element.id === preparation.id ? preparation : element
      )
    );
  }

  async function creer(event: FormEvent) {
    event.preventDefault();
    const response = await fetch(`${API_URL}/api/preparations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        affaire_id: Number(form.affaire_id),
        nom: form.nom,
        date_besoin: form.date_besoin || null,
        demandeur: form.demandeur || null,
        preparateur: form.preparateur || null,
        vehicule: form.vehicule || null,
        commentaire: form.commentaire || null,
      }),
    });

    if (!response.ok) {
      setToast({ type: "error", message: "Création impossible." });
      return;
    }

    const preparation = await response.json();
    setModalOuverte(false);
    setForm(formulaireVide);
    ouvrirPreparation(preparation);
    await charger();
  }

  async function modifierEntete(event: FormEvent) {
    event.preventDefault();
    if (!selection) return;

    const response = await fetch(
      `${API_URL}/api/preparations/${selection.id}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nom: form.nom,
          date_besoin: form.date_besoin || null,
          demandeur: form.demandeur || null,
          preparateur: form.preparateur || null,
          vehicule: form.vehicule || null,
          commentaire: form.commentaire || null,
        }),
      }
    );

    if (!response.ok) {
      setToast({ type: "error", message: "Modification impossible." });
      return;
    }

    const preparation = await response.json();
    await actualiserSelection(preparation);
    setEditionEntete(false);
  }

  async function enregistrerLigne(event: FormEvent) {
    event.preventDefault();
    if (!selection) return;

    const url = ligneEditee
      ? `${API_URL}/api/preparations/${selection.id}/lignes/${ligneEditee.id}`
      : `${API_URL}/api/preparations/${selection.id}/lignes`;

    const response = await fetch(url, {
      method: ligneEditee ? "PATCH" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...(ligneEditee
          ? {}
          : { article_id: Number(ligneForm.article_id) }),
        lot_id: ligneForm.lot_id ? Number(ligneForm.lot_id) : null,
        emplacement_source_id: ligneForm.emplacement_source_id
          ? Number(ligneForm.emplacement_source_id)
          : null,
        quantite_demandee: Number(ligneForm.quantite_demandee),
        commentaire: ligneForm.commentaire || null,
      }),
    });

    if (!response.ok) {
      const detail = await response.json().catch(() => null);
      setToast({
        type: "error",
        message: detail?.detail ?? "Enregistrement impossible.",
      });
      return;
    }

    const preparation = await response.json();
    await actualiserSelection(preparation);
    setLigneEditee(null);
    setLigneForm(ligneVide);
  }

  function editerLigne(ligne: Ligne) {
    setLigneEditee(ligne);
    setLigneForm({
      article_id: String(ligne.article_id),
      lot_id: ligne.lot_id ? String(ligne.lot_id) : "",
      emplacement_source_id: ligne.emplacement_source_id
        ? String(ligne.emplacement_source_id)
        : "",
      quantite_demandee: ligne.quantite_demandee,
      commentaire: ligne.commentaire ?? "",
    });
  }

  async function supprimerLigne(ligne: Ligne) {
    if (!selection) return;
    const response = await fetch(
      `${API_URL}/api/preparations/${selection.id}/lignes/${ligne.id}`,
      { method: "DELETE" }
    );

    if (!response.ok) {
      setToast({ type: "error", message: "Suppression impossible." });
      return;
    }
    await actualiserSelection(await response.json());
  }

  async function saisirPreparee(ligne: Ligne, valeur: string) {
    if (!selection) return;

    const response = await fetch(
      `${API_URL}/api/preparations/${selection.id}/lignes/${ligne.id}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quantite_preparee: Number(valeur),
        }),
      }
    );

    if (response.ok) {
      await actualiserSelection(await response.json());
    }
  }


  async function supprimerPreparation() {
    if (!selection) return;

    const confirmation = window.confirm(
      `Supprimer définitivement ${selection.reference} ?\n\n` +
        "Les réservations associées seront libérées. " +
        "Cette action est impossible pour une préparation expédiée."
    );

    if (!confirmation) return;

    const response = await fetch(
      `${API_URL}/api/preparations/${selection.id}`,
      { method: "DELETE" }
    );

    if (!response.ok) {
      const detail = await response.json().catch(() => null);
      setToast({
        type: "error",
        message: detail?.detail ?? "Suppression impossible.",
      });
      return;
    }

    setPreparations((actuelles) =>
      actuelles.filter(
        (preparation) => preparation.id !== selection.id
      )
    );
    setSelection(null);
    setEditionEntete(false);
    setLigneEditee(null);
    setLigneForm(ligneVide);
    setToast({
      type: "success",
      message: `${selection.reference} supprimée. Les réservations ont été libérées.`,
    });
  }


  async function action(actionName: string) {
    if (!selection) return;

    const response = await fetch(
      `${API_URL}/api/preparations/${selection.id}/${actionName}`,
      { method: "POST" }
    );

    if (!response.ok) {
      const detail = await response.json().catch(() => null);
      setToast({
        type: "error",
        message: detail?.detail ?? "Action impossible.",
      });
      return;
    }

    const preparation = await response.json();
    await actualiserSelection(preparation);
    setToast({
      type: "success",
      message: `${preparation.reference} mise à jour.`,
    });
  }

  return (
    <div>
      <div className="breadcrumb">Exploitation / Préparations</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Flux chantier</span>
          <h1>Préparations</h1>
          <p>
            Les besoins validés génèrent automatiquement les réservations.
          </p>
        </div>

        <Button
          variant="secondary"
          onClick={() => {
            setForm(formulaireVide);
            setModalOuverte(true);
          }}
        >
          <Plus size={18} />
          Nouvelle préparation
        </Button>
      </div>

      <section className="content-card">
        <div className={styles.filters}>
          <label className="search-field">
            <Search size={17} />
            <input
              type="search"
              placeholder="Référence, affaire, client, demandeur ou préparateur"
              value={recherche}
              onChange={(event) => setRecherche(event.target.value)}
            />
          </label>

          <select
            value={filtreStatut}
            onChange={(event) => setFiltreStatut(event.target.value)}
          >
            <option value="">Tous les statuts</option>
            <option value="BROUILLON">Brouillon</option>
            <option value="VALIDEE">Validée</option>
            <option value="EN_PREPARATION">En préparation</option>
            <option value="PRETE">Prête</option>
            <option value="EXPEDIEE">Expédiée</option>
          </select>

          <span className={styles.resultCount}>
            {preparationsFiltrees.length} préparation(s)
          </span>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Affaire</th>
                <th>Client</th>
                <th>Site / Zone</th>
                <th>Demandeur</th>
                <th>Préparateur</th>
                <th>Début</th>
                <th>Fin prévue</th>
                <th>Avancement</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {preparationsFiltrees.map((preparation) => {
                const statut = statutPreparation(preparation.statut);
                const avancement = progression(preparation);

                return (
                  <tr
                    key={preparation.id}
                    className="clickable-row"
                    onClick={() => ouvrirPreparation(preparation)}
                  >
                    <td>
                      <span className="reference-chip">
                        {preparation.reference}
                      </span>
                      <strong className="table-title">
                        {preparation.nom}
                      </strong>
                    </td>
                    <td>
                      <strong>
                        {preparation.affaire.code_externe ||
                          preparation.affaire.reference}
                      </strong>
                      <small className="table-subtext">
                        {preparation.affaire.nom}
                      </small>
                    </td>
                    <td>{preparation.affaire.client ?? "—"}</td>
                    <td>
                      <strong>{preparation.affaire.site ?? "—"}</strong>
                      <small className="table-subtext">
                        {preparation.affaire.zone_intervention ?? "—"}
                      </small>
                    </td>
                    <td>{preparation.demandeur ?? "—"}</td>
                    <td>{preparation.preparateur ?? "—"}</td>
                    <td>
                      {formaterDate(
                        preparation.date_besoin ||
                          preparation.affaire.date_debut
                      )}
                    </td>
                    <td>
                      {formaterDate(preparation.affaire.date_fin_prevue)}
                    </td>
                    <td>
                      <div className={styles.progressCell}>
                        <div className={styles.progressTrack}>
                          <span style={{ width: `${avancement}%` }} />
                        </div>
                        <small>
                          {avancement}% · {preparation.lignes.length} ligne(s)
                        </small>
                      </div>
                    </td>
                    <td>
                      <Badge tone={statut.tone}>{statut.label}</Badge>
                    </td>
                  </tr>
                );
              })}

              {preparationsFiltrees.length === 0 && (
                <tr>
                  <td colSpan={10} className="empty-state">
                    <strong>Aucune préparation trouvée</strong>
                    <span>
                      Modifiez les filtres ou créez une nouvelle préparation.
                    </span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <Drawer
        open={selection !== null}
        title={selection?.reference ?? ""}
        onClose={() => setSelection(null)}
      >
        {selection && (
          <div>
            <div className={styles.detailHeader}>
              <div>
                <h3>{selection.nom}</h3>
                <p>
                  {selection.affaire.code_externe ||
                    selection.affaire.reference}{" "}
                  — {selection.affaire.nom}
                </p>
              </div>
              <strong>{selection.statut}</strong>
            </div>

            {editable && (
              <div className={styles.editHeaderButton}>
                <Button
                  variant="secondary"
                  onClick={() => setEditionEntete(!editionEntete)}
                >
                  <Pencil size={16} />
                  Modifier la commande
                </Button>
              </div>
            )}

            {editionEntete && (
              <form className={styles.headerForm} onSubmit={modifierEntete}>
                <input
                  required
                  placeholder="Nom"
                  value={form.nom}
                  onChange={(event) =>
                    setForm({ ...form, nom: event.target.value })
                  }
                />
                <input
                  type="date"
                  value={form.date_besoin}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      date_besoin: event.target.value,
                    })
                  }
                />
                <input
                  placeholder="Demandeur"
                  value={form.demandeur}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      demandeur: event.target.value,
                    })
                  }
                />
                <input
                  placeholder="Préparateur"
                  value={form.preparateur}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      preparateur: event.target.value,
                    })
                  }
                />
                <input
                  placeholder="Véhicule"
                  value={form.vehicule}
                  onChange={(event) =>
                    setForm({ ...form, vehicule: event.target.value })
                  }
                />
                <Button type="submit">Enregistrer</Button>
              </form>
            )}

            {editable && (
              <form className={styles.addLine} onSubmit={enregistrerLigne}>
                <h4>
                  {ligneEditee
                    ? "Modifier le besoin"
                    : "Ajouter un article"}
                </h4>

                <select
                  required
                  disabled={ligneEditee !== null}
                  value={ligneForm.article_id}
                  onChange={(event) =>
                    setLigneForm({
                      ...ligneForm,
                      article_id: event.target.value,
                      lot_id: "",
                    })
                  }
                >
                  <option value="">Article</option>
                  {articles.map((article) => (
                    <option key={article.id} value={article.id}>
                      {article.reference} — {article.designation}
                    </option>
                  ))}
                </select>

                {articleEstBeton && (
                  <select
                    required
                    value={ligneForm.lot_id}
                    onChange={(event) =>
                      setLigneForm({
                        ...ligneForm,
                        lot_id: event.target.value,
                      })
                    }
                  >
                    <option value="">Lot béton</option>
                    {lotsArticle.map((lot) => (
                      <option key={lot.id} value={lot.id}>
                        {lot.numero_lot_fournisseur}
                      </option>
                    ))}
                  </select>
                )}

                <select
                  required
                  value={ligneForm.emplacement_source_id}
                  onChange={(event) =>
                    setLigneForm({
                      ...ligneForm,
                      emplacement_source_id: event.target.value,
                    })
                  }
                >
                  <option value="">Emplacement source</option>
                  {emplacements.map((emplacement) => (
                    <option key={emplacement.id} value={emplacement.id}>
                      {emplacement.nom}
                    </option>
                  ))}
                </select>

                <input
                  required
                  type="number"
                  min="0.001"
                  step="0.001"
                  placeholder="Quantité demandée"
                  value={ligneForm.quantite_demandee}
                  onChange={(event) =>
                    setLigneForm({
                      ...ligneForm,
                      quantite_demandee: event.target.value,
                    })
                  }
                />

                <div className={styles.lineFormActions}>
                  {ligneEditee && (
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => {
                        setLigneEditee(null);
                        setLigneForm(ligneVide);
                      }}
                    >
                      Annuler
                    </Button>
                  )}
                  <Button type="submit" variant="secondary">
                    {ligneEditee ? "Modifier" : "Ajouter"}
                  </Button>
                </div>
              </form>
            )}

            <div className={styles.lines}>
              {selection.lignes.map((ligne) => (
                <div className={styles.line} key={ligne.id}>
                  <div>
                    <strong>{ligne.article.designation}</strong>
                    <span>
                      {ligne.article.reference}
                      {ligne.lot
                        ? ` — Lot ${ligne.lot.numero_lot_fournisseur}`
                        : ""}
                    </span>
                    <small>
                      {ligne.emplacement_source?.nom ?? "Source à définir"}
                    </small>
                  </div>

                  <div className={styles.quantities}>
                    <label>
                      <span>Demandé</span>
                      <strong>
                        {Number(ligne.quantite_demandee).toLocaleString("fr-FR")}{" "}
                        {ligne.article.unite}
                      </strong>
                    </label>

                    <label>
                      <span>Préparé</span>
                      <input
                        type="number"
                        min="0"
                        step="0.001"
                        disabled={
                          selection.statut !== "EN_PREPARATION"
                        }
                        defaultValue={ligne.quantite_preparee}
                        onBlur={(event) =>
                          saisirPreparee(ligne, event.target.value)
                        }
                      />
                    </label>
                  </div>

                  {editable && (
                    <div className={styles.lineActions}>
                      <button onClick={() => editerLigne(ligne)}>
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => supprimerLigne(ligne)}>
                        <Trash2 size={15} />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="drawer-actions">
              {selection.statut === "BROUILLON" && (
                <Button onClick={() => action("valider")}>
                  <CheckCircle2 size={17} />
                  Valider et réserver
                </Button>
              )}
              {selection.statut === "VALIDEE" && (
                <Button onClick={() => action("demarrer")}>
                  <Play size={17} />
                  Démarrer
                </Button>
              )}
              {selection.statut === "EN_PREPARATION" && (
                <Button onClick={() => action("terminer")}>
                  Marquer prête
                </Button>
              )}
              {selection.statut === "PRETE" && (
                <Button onClick={() => action("expedier")}>
                  <Send size={17} />
                  Expédier
                </Button>
              )}

              {selection.statut !== "EXPEDIEE" && (
                <Button
                  variant="ghost"
                  onClick={supprimerPreparation}
                >
                  <XCircle size={17} />
                  Supprimer la préparation
                </Button>
              )}
            </div>
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
                <span className="eyebrow">Nouvelle préparation</span>
                <h2>Créer une préparation chantier</h2>
              </div>
            </div>

            <form onSubmit={creer}>
              <div className="form-grid">
                <label className="field field-wide">
                  <span>Affaire *</span>
                  <select
                    required
                    value={form.affaire_id}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        affaire_id: event.target.value,
                      })
                    }
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
                  <span>Nom *</span>
                  <input
                    required
                    value={form.nom}
                    onChange={(event) =>
                      setForm({ ...form, nom: event.target.value })
                    }
                  />
                </label>

                <label className="field">
                  <span>Date de besoin</span>
                  <input
                    type="date"
                    value={form.date_besoin}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        date_besoin: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Véhicule</span>
                  <input
                    value={form.vehicule}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        vehicule: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Demandeur</span>
                  <input
                    value={form.demandeur}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        demandeur: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Préparateur</span>
                  <input
                    value={form.preparateur}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        preparateur: event.target.value,
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
                <Button type="submit">Créer la préparation</Button>
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
