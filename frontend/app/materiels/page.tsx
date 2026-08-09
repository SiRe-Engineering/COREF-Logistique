"use client";

import { apiFetch } from "@/lib/api";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CalendarClock,
  Hammer,
  Pencil,
  Plus,
  Search,
  Wrench,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Toast } from "@/components/ui/Toast";
import { MaterielTabs } from "@/components/materiel/MaterielTabs";
import styles from "./page.module.css";

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
  statut: string;
};

type Materiel = {
  id: number;
  numero_inventaire: string;
  designation: string;
  categorie: string;
  marque: string | null;
  modele: string | null;
  numero_serie: string | null;
  etat: string;
  emplacement_id: number | null;
  affaire_id: number | null;
  date_achat: string | null;
  valeur_achat: string | null;
  date_dernier_controle: string | null;
  date_prochain_controle: string | null;
  type_controle: string | null;
  commentaire: string | null;
  actif: boolean;
  emplacement: Emplacement | null;
  affaire: Affaire | null;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const categories = [
  "Malaxeur",
  "Scie à briques",
  "Électroportatif",
  "Air comprimé",
  "Levage",
  "Mesure",
  "Outillage",
  "Autre",
];

const etats = [
  { value: "DISPONIBLE", label: "Disponible" },
  { value: "EN_CHANTIER", label: "En chantier" },
  { value: "EN_PRET", label: "En déplacement" },
  { value: "EN_MAINTENANCE", label: "En maintenance" },
  { value: "HORS_SERVICE", label: "Hors service" },
  { value: "PERDU", label: "Perdu" },
];

const initialForm = {
  designation: "",
  categorie: "Malaxeur",
  marque: "",
  modele: "",
  numero_serie: "",
  etat: "DISPONIBLE",
  emplacement_id: "",
  affaire_id: "",
  date_achat: "",
  valeur_achat: "",
  date_dernier_controle: "",
  date_prochain_controle: "",
  type_controle: "",
  commentaire: "",
};

function statutMateriel(etat: string) {
  if (etat === "DISPONIBLE") {
    return { label: "Disponible", tone: "success" as const };
  }
  if (etat === "EN_CHANTIER") {
    return { label: "En chantier", tone: "isolants" as const };
  }
  if (etat === "EN_PRET") {
    return { label: "En déplacement", tone: "isolants" as const };
  }
  if (etat === "EN_MAINTENANCE") {
    return { label: "Maintenance", tone: "warning" as const };
  }
  if (etat === "PERDU") {
    return { label: "Perdu", tone: "beton" as const };
  }
  return {
    label: "Hors service",
    tone: "beton" as const,
  };
}

function versFormulaire(materiel: Materiel) {
  return {
    designation: materiel.designation,
    categorie: materiel.categorie,
    marque: materiel.marque ?? "",
    modele: materiel.modele ?? "",
    numero_serie: materiel.numero_serie ?? "",
    etat: materiel.etat,
    emplacement_id: materiel.emplacement_id
      ? String(materiel.emplacement_id)
      : "",
    affaire_id: materiel.affaire_id
      ? String(materiel.affaire_id)
      : "",
    date_achat: materiel.date_achat ?? "",
    valeur_achat: materiel.valeur_achat ?? "",
    date_dernier_controle: materiel.date_dernier_controle ?? "",
    date_prochain_controle: materiel.date_prochain_controle ?? "",
    type_controle: materiel.type_controle ?? "",
    commentaire: materiel.commentaire ?? "",
  };
}

function joursAvant(date: string | null) {
  if (!date) return null;

  const aujourdHui = new Date();
  aujourdHui.setHours(0, 0, 0, 0);

  const cible = new Date(`${date}T00:00:00`);
  return Math.ceil(
    (cible.getTime() - aujourdHui.getTime()) / 86_400_000
  );
}


type FormulaireMaterielProps = {
  form: typeof initialForm;
  setForm: React.Dispatch<React.SetStateAction<typeof initialForm>>;
  emplacements: Emplacement[];
  affaires: Affaire[];
};

function FormulaireMateriel({
  form,
  setForm,
  emplacements,
  affaires,
}: FormulaireMaterielProps) {
  return (
    <div className="form-grid">
      <label className="field field-wide">
        <span>Désignation *</span>
        <input
          required
          maxLength={200}
          value={form.designation}
          onChange={(event) =>
            setForm({ ...form, designation: event.target.value })
          }
        />
      </label>

      <label className="field">
        <span>Catégorie *</span>
        <select
          required
          value={form.categorie}
          onChange={(event) =>
            setForm({ ...form, categorie: event.target.value })
          }
        >
          {categories.map((categorie) => (
            <option key={categorie}>{categorie}</option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>État *</span>
        <select
          required
          value={form.etat}
          onChange={(event) =>
            setForm({
              ...form,
              etat: event.target.value,
              affaire_id:
                event.target.value === "EN_CHANTIER"
                  ? form.affaire_id
                  : "",
            })
          }
        >
          {etats.map((etat) => (
            <option key={etat.value} value={etat.value}>
              {etat.label}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Marque</span>
        <input
          maxLength={120}
          value={form.marque}
          onChange={(event) =>
            setForm({ ...form, marque: event.target.value })
          }
        />
      </label>

      <label className="field">
        <span>Modèle</span>
        <input
          maxLength={120}
          value={form.modele}
          onChange={(event) =>
            setForm({ ...form, modele: event.target.value })
          }
        />
      </label>

      <label className="field field-wide">
        <span>Numéro de série</span>
        <input
          maxLength={150}
          value={form.numero_serie}
          onChange={(event) =>
            setForm({ ...form, numero_serie: event.target.value })
          }
        />
      </label>

      <label className="field">
        <span>Emplacement</span>
        <select
          value={form.emplacement_id}
          onChange={(event) =>
            setForm({
              ...form,
              emplacement_id: event.target.value,
            })
          }
        >
          <option value="">Non renseigné</option>
          {emplacements.map((emplacement) => (
            <option key={emplacement.id} value={emplacement.id}>
              {emplacement.nom} — {emplacement.code}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Affaire</span>
        <select
          value={form.affaire_id}
          required={form.etat === "EN_CHANTIER"}
          disabled={form.etat !== "EN_CHANTIER"}
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
                !["TERMINEE", "ANNULEE"].includes(affaire.statut)
            )
            .map((affaire) => (
              <option key={affaire.id} value={affaire.id}>
                {affaire.code_externe || affaire.reference} —{" "}
                {affaire.nom}
              </option>
            ))}
        </select>
      </label>

      <label className="field">
        <span>Date d’achat</span>
        <input
          type="date"
          value={form.date_achat}
          onChange={(event) =>
            setForm({ ...form, date_achat: event.target.value })
          }
        />
      </label>

      <label className="field">
        <span>Valeur d’achat (€)</span>
        <input
          type="number"
          min="0"
          step="0.01"
          value={form.valeur_achat}
          onChange={(event) =>
            setForm({ ...form, valeur_achat: event.target.value })
          }
        />
      </label>

      <label className="field">
        <span>Dernier contrôle</span>
        <input
          type="date"
          value={form.date_dernier_controle}
          onChange={(event) =>
            setForm({
              ...form,
              date_dernier_controle: event.target.value,
            })
          }
        />
      </label>

      <label className="field">
        <span>Prochain contrôle</span>
        <input
          type="date"
          value={form.date_prochain_controle}
          onChange={(event) =>
            setForm({
              ...form,
              date_prochain_controle: event.target.value,
            })
          }
        />
      </label>

      <label className="field field-wide">
        <span>Type de contrôle</span>
        <input
          maxLength={120}
          placeholder="Ex. Vérification électrique annuelle"
          value={form.type_controle}
          onChange={(event) =>
            setForm({
              ...form,
              type_controle: event.target.value,
            })
          }
        />
      </label>

      <label className="field field-wide">
        <span>Commentaire</span>
        <textarea
          className={styles.textarea}
          rows={4}
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
  );
}


export default function MaterielsPage() {
  const [materiels, setMateriels] = useState<Materiel[]>([]);
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [affaires, setAffaires] = useState<Affaire[]>([]);
  const [recherche, setRecherche] = useState("");
  const [filtreEtat, setFiltreEtat] = useState("");
  const [modalCreationOuverte, setModalCreationOuverte] = useState(false);
  const [materielSelectionne, setMaterielSelectionne] =
    useState<Materiel | null>(null);
  const [modeEdition, setModeEdition] = useState(false);
  const [enregistrement, setEnregistrement] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const [materielsResponse, emplacementsResponse, affairesResponse] =
        await Promise.all([
          apiFetch(`${API_URL}/api/materiels`),
          apiFetch(`${API_URL}/api/emplacements?racines_uniquement=false`),
          apiFetch(`${API_URL}/api/affaires`),
        ]);

      if (
        !materielsResponse.ok ||
        !emplacementsResponse.ok ||
        !affairesResponse.ok
      ) {
        throw new Error();
      }

      const [materielsData, emplacementsData, affairesData] =
        await Promise.all([
          materielsResponse.json(),
          emplacementsResponse.json(),
          affairesResponse.json(),
        ]);

      setMateriels(materielsData);
      setEmplacements(emplacementsData);
      setAffaires(affairesData);
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger le parc matériel.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const materielsFiltres = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    return materiels.filter((materiel) => {
      const correspondRecherche =
        !terme ||
        materiel.numero_inventaire.toLowerCase().includes(terme) ||
        materiel.designation.toLowerCase().includes(terme) ||
        materiel.categorie.toLowerCase().includes(terme) ||
        (materiel.marque ?? "").toLowerCase().includes(terme) ||
        (materiel.modele ?? "").toLowerCase().includes(terme) ||
        (materiel.numero_serie ?? "").toLowerCase().includes(terme);

      const correspondEtat =
        !filtreEtat || materiel.etat === filtreEtat;

      return correspondRecherche && correspondEtat;
    });
  }, [materiels, recherche, filtreEtat]);

  const controlesAlerte = materiels.filter((materiel) => {
    const jours = joursAvant(materiel.date_prochain_controle);
    return jours !== null && jours <= 30;
  }).length;

  function ouvrirCreation() {
    setForm(initialForm);
    setModalCreationOuverte(true);
  }

  function ouvrirMateriel(materiel: Materiel) {
    setMaterielSelectionne(materiel);
    setForm(versFormulaire(materiel));
    setModeEdition(false);
  }

  function fermerDrawer() {
    setMaterielSelectionne(null);
    setModeEdition(false);
    setForm(initialForm);
  }

  function payloadFormulaire() {
    return {
      designation: form.designation,
      categorie: form.categorie,
      marque: form.marque || null,
      modele: form.modele || null,
      numero_serie: form.numero_serie || null,
      etat: form.etat,
      emplacement_id: form.emplacement_id
        ? Number(form.emplacement_id)
        : null,
      affaire_id: form.affaire_id
        ? Number(form.affaire_id)
        : null,
      date_achat: form.date_achat || null,
      valeur_achat: form.valeur_achat
        ? Number(form.valeur_achat)
        : null,
      date_dernier_controle: form.date_dernier_controle || null,
      date_prochain_controle: form.date_prochain_controle || null,
      type_controle: form.type_controle || null,
      commentaire: form.commentaire || null,
    };
  }

  async function creer(event: FormEvent) {
    event.preventDefault();
    setEnregistrement(true);

    try {
      const response = await apiFetch(`${API_URL}/api/materiels`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payloadFormulaire()),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(
          typeof detail?.detail === "string"
            ? detail.detail
            : "Création impossible."
        );
      }

      const materiel: Materiel = await response.json();

      setModalCreationOuverte(false);
      setForm(initialForm);
      setToast({
        type: "success",
        message: `${materiel.numero_inventaire} créé.`,
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
    } finally {
      setEnregistrement(false);
    }
  }

  async function modifier(event: FormEvent) {
    event.preventDefault();

    if (!materielSelectionne) return;

    setEnregistrement(true);

    try {
      const response = await apiFetch(
        `${API_URL}/api/materiels/${materielSelectionne.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payloadFormulaire()),
        }
      );

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(
          typeof detail?.detail === "string"
            ? detail.detail
            : "Modification impossible."
        );
      }

      const materielModifie: Materiel = await response.json();

      setMateriels((actuels) =>
        actuels.map((materiel) =>
          materiel.id === materielModifie.id
            ? materielModifie
            : materiel
        )
      );
      setMaterielSelectionne(materielModifie);
      setForm(versFormulaire(materielModifie));
      setModeEdition(false);
      setToast({
        type: "success",
        message: `${materielModifie.numero_inventaire} mis à jour.`,
      });
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Modification impossible.",
      });
    } finally {
      setEnregistrement(false);
    }
  }



  return (
    <div>
      <div className="breadcrumb">Parc / Matériels</div><MaterielTabs />

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Parc matériel</span>
          <h1>Matériels</h1>
          <p>
            Localisez les équipements, suivez leur état et leurs contrôles.
          </p>
        </div>

        <Button variant="secondary" onClick={ouvrirCreation}>
          <Plus size={18} />
          Nouveau matériel
        </Button>
      </div>

      <section className={styles.summary}>
        <article>
          <Hammer size={20} />
          <div>
            <span>Matériels actifs</span>
            <strong>{materiels.length}</strong>
          </div>
        </article>
        <article>
          <Wrench size={20} />
          <div>
            <span>En maintenance</span>
            <strong>
              {
                materiels.filter(
                  (materiel) => materiel.etat === "EN_MAINTENANCE"
                ).length
              }
            </strong>
          </div>
        </article>
        <article>
          <CalendarClock size={20} />
          <div>
            <span>Contrôles sous 30 jours</span>
            <strong>{controlesAlerte}</strong>
          </div>
        </article>
        <article>
          <AlertTriangle size={20} />
          <div>
            <span>Hors service / perdus</span>
            <strong>
              {
                materiels.filter((materiel) =>
                  ["HORS_SERVICE", "PERDU"].includes(materiel.etat)
                ).length
              }
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
              placeholder="Inventaire, désignation, marque ou série"
              value={recherche}
              onChange={(event) => setRecherche(event.target.value)}
            />
          </label>

          <select
            value={filtreEtat}
            onChange={(event) => setFiltreEtat(event.target.value)}
          >
            <option value="">Tous les états</option>
            {etats.map((etat) => (
              <option key={etat.value} value={etat.value}>
                {etat.label}
              </option>
            ))}
          </select>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Inventaire</th>
                <th>Matériel</th>
                <th>Catégorie</th>
                <th>Localisation</th>
                <th>Affectation</th>
                <th>Prochain contrôle</th>
                <th>État</th>
              </tr>
            </thead>
            <tbody>
              {materielsFiltres.map((materiel) => {
                const statut = statutMateriel(materiel.etat);
                const jours = joursAvant(materiel.date_prochain_controle);

                return (
                  <tr
                    key={materiel.id}
                    className="clickable-row"
                    onClick={() => ouvrirMateriel(materiel)}
                  >
                    <td>
                      <span className="reference-chip">
                        {materiel.numero_inventaire}
                      </span>
                    </td>
                    <td>
                      <div className={styles.materielCell}>
                        <strong>{materiel.designation}</strong>
                        <small>
                          {[materiel.marque, materiel.modele]
                            .filter(Boolean)
                            .join(" ") || "—"}
                        </small>
                      </div>
                    </td>
                    <td>{materiel.categorie}</td>
                    <td>{materiel.emplacement?.nom ?? "—"}</td>
                    <td>
                      {materiel.affaire
                        ? materiel.affaire.code_externe ||
                          materiel.affaire.reference
                        : "—"}
                    </td>
                    <td>
                      {materiel.date_prochain_controle ? (
                        <span
                          className={
                            jours !== null && jours <= 30
                              ? styles.controlAlert
                              : ""
                          }
                        >
                          {new Intl.DateTimeFormat("fr-FR").format(
                            new Date(
                              `${materiel.date_prochain_controle}T00:00:00`
                            )
                          )}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      <Badge tone={statut.tone}>{statut.label}</Badge>
                    </td>
                  </tr>
                );
              })}

              {materielsFiltres.length === 0 && (
                <tr>
                  <td colSpan={7} className="empty-state">
                    <Hammer size={24} />
                    <strong>Aucun matériel</strong>
                    <span>Créez le premier équipement du parc.</span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <Drawer
        open={materielSelectionne !== null}
        title={materielSelectionne?.numero_inventaire ?? ""}
        onClose={fermerDrawer}
      >
        {materielSelectionne && !modeEdition && (
          <div className={styles.detail}>
            <div className={styles.detailHeader}>
              <div>
                <h3>{materielSelectionne.designation}</h3>
                <p>
                  {[materielSelectionne.marque, materielSelectionne.modele]
                    .filter(Boolean)
                    .join(" ") || "Marque et modèle non renseignés"}
                </p>
              </div>
              <Badge tone={statutMateriel(materielSelectionne.etat).tone}>
                {statutMateriel(materielSelectionne.etat).label}
              </Badge>
            </div>

            <dl className="detail-grid">
              <div>
                <dt>Catégorie</dt>
                <dd>{materielSelectionne.categorie}</dd>
              </div>
              <div>
                <dt>Numéro de série</dt>
                <dd>{materielSelectionne.numero_serie ?? "—"}</dd>
              </div>
              <div>
                <dt>Emplacement</dt>
                <dd>{materielSelectionne.emplacement?.nom ?? "—"}</dd>
              </div>
              <div>
                <dt>Affaire</dt>
                <dd>
                  {materielSelectionne.affaire
                    ? materielSelectionne.affaire.code_externe ||
                      materielSelectionne.affaire.reference
                    : "—"}
                </dd>
              </div>
              <div>
                <dt>Dernier contrôle</dt>
                <dd>{materielSelectionne.date_dernier_controle ?? "—"}</dd>
              </div>
              <div>
                <dt>Prochain contrôle</dt>
                <dd>{materielSelectionne.date_prochain_controle ?? "—"}</dd>
              </div>
            </dl>

            {materielSelectionne.type_controle && (
              <section className="drawer-section">
                <h4>Contrôle</h4>
                <div className="placeholder-panel">
                  {materielSelectionne.type_controle}
                </div>
              </section>
            )}

            <div className="drawer-actions">
              <Button
                variant="secondary"
                onClick={() => {
                  setForm(versFormulaire(materielSelectionne));
                  setModeEdition(true);
                }}
              >
                <Pencil size={17} />
                Modifier le matériel
              </Button>
            </div>
          </div>
        )}

        {materielSelectionne && modeEdition && (
          <form onSubmit={modifier}>
            <FormulaireMateriel
              form={form}
              setForm={setForm}
              emplacements={emplacements}
              affaires={affaires}
            />

            <div className="modal-actions">
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  setForm(versFormulaire(materielSelectionne));
                  setModeEdition(false);
                }}
                disabled={enregistrement}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={enregistrement}>
                {enregistrement
                  ? "Enregistrement…"
                  : "Enregistrer les modifications"}
              </Button>
            </div>
          </form>
        )}
      </Drawer>

      {modalCreationOuverte && (
        <div
          className="modal-backdrop"
          onMouseDown={() => setModalCreationOuverte(false)}
        >
          <section
            className="modal-card"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">Nouvel équipement</span>
                <h2>Créer un matériel</h2>
                <p>
                  Le numéro d’inventaire sera généré automatiquement.
                </p>
              </div>
            </div>

            <form onSubmit={creer}>
              <FormulaireMateriel
              form={form}
              setForm={setForm}
              emplacements={emplacements}
              affaires={affaires}
            />

              <div className="modal-actions">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setModalCreationOuverte(false)}
                  disabled={enregistrement}
                >
                  Annuler
                </Button>
                <Button type="submit" disabled={enregistrement}>
                  {enregistrement ? "Création…" : "Créer le matériel"}
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
