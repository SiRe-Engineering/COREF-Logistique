"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  BriefcaseBusiness,
  Building2,
  CalendarDays,
  Pencil,
  Plus,
  Search,
  UserRound,
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
  statut: string;
  date_debut: string | null;
  date_fin_prevue: string | null;
  commentaire: string | null;
  actif: boolean;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const statuts = [
  { value: "OUVERTE", label: "Ouverte" },
  { value: "EN_PREPARATION", label: "En préparation" },
  { value: "EN_COURS", label: "En cours" },
  { value: "TERMINEE", label: "Terminée" },
  { value: "ANNULEE", label: "Annulée" },
];

const initialForm = {
  code_externe: "",
  nom: "",
  client: "",
  site: "",
  zone_intervention: "",
  charge_affaires: "",
  statut: "OUVERTE",
  date_debut: "",
  date_fin_prevue: "",
  commentaire: "",
};

function statutAffaire(statut: string) {
  if (statut === "EN_COURS") {
    return { label: "En cours", tone: "success" as const };
  }
  if (statut === "EN_PREPARATION") {
    return { label: "Préparation", tone: "warning" as const };
  }
  if (statut === "TERMINEE") {
    return { label: "Terminée", tone: "neutral" as const };
  }
  if (statut === "ANNULEE") {
    return { label: "Annulée", tone: "beton" as const };
  }
  return { label: "Ouverte", tone: "isolants" as const };
}

function versFormulaire(affaire: Affaire) {
  return {
    code_externe: affaire.code_externe ?? "",
    nom: affaire.nom,
    client: affaire.client ?? "",
    site: affaire.site ?? "",
    zone_intervention: affaire.zone_intervention ?? "",
    charge_affaires: affaire.charge_affaires ?? "",
    statut: affaire.statut,
    date_debut: affaire.date_debut ?? "",
    date_fin_prevue: affaire.date_fin_prevue ?? "",
    commentaire: affaire.commentaire ?? "",
  };
}

export default function AffairesPage() {
  const [affaires, setAffaires] = useState<Affaire[]>([]);
  const [recherche, setRecherche] = useState("");
  const [filtreStatut, setFiltreStatut] = useState("");
  const [modalCreationOuverte, setModalCreationOuverte] = useState(false);
  const [affaireSelectionnee, setAffaireSelectionnee] =
    useState<Affaire | null>(null);
  const [modeEdition, setModeEdition] = useState(false);
  const [enregistrement, setEnregistrement] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const response = await fetch(`${API_URL}/api/affaires`);
      if (!response.ok) throw new Error();
      setAffaires(await response.json());
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger les affaires.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const affairesFiltrees = useMemo(() => {
    const terme = recherche.trim().toLowerCase();

    return affaires.filter((affaire) => {
      const correspondRecherche =
        !terme ||
        affaire.reference.toLowerCase().includes(terme) ||
        (affaire.code_externe ?? "").toLowerCase().includes(terme) ||
        affaire.nom.toLowerCase().includes(terme) ||
        (affaire.client ?? "").toLowerCase().includes(terme) ||
        (affaire.site ?? "").toLowerCase().includes(terme) ||
        (affaire.charge_affaires ?? "").toLowerCase().includes(terme);

      const correspondStatut =
        !filtreStatut || affaire.statut === filtreStatut;

      return correspondRecherche && correspondStatut;
    });
  }, [affaires, recherche, filtreStatut]);

  function ouvrirCreation() {
    setForm(initialForm);
    setModalCreationOuverte(true);
  }

  function ouvrirAffaire(affaire: Affaire) {
    setAffaireSelectionnee(affaire);
    setForm(versFormulaire(affaire));
    setModeEdition(false);
  }

  function fermerDrawer() {
    setAffaireSelectionnee(null);
    setModeEdition(false);
    setForm(initialForm);
  }

  async function creer(event: FormEvent) {
    event.preventDefault();
    setEnregistrement(true);

    try {
      const response = await fetch(`${API_URL}/api/affaires`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code_externe: form.code_externe || null,
          nom: form.nom,
          client: form.client || null,
          site: form.site || null,
          zone_intervention: form.zone_intervention || null,
          charge_affaires: form.charge_affaires || null,
          statut: form.statut,
          date_debut: form.date_debut || null,
          date_fin_prevue: form.date_fin_prevue || null,
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

      const affaire: Affaire = await response.json();

      setModalCreationOuverte(false);
      setForm(initialForm);
      setToast({
        type: "success",
        message: `${affaire.reference} créée.`,
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

    if (!affaireSelectionnee) return;

    setEnregistrement(true);

    try {
      const response = await fetch(
        `${API_URL}/api/affaires/${affaireSelectionnee.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            code_externe: form.code_externe || null,
            nom: form.nom,
            client: form.client || null,
            site: form.site || null,
            zone_intervention: form.zone_intervention || null,
            charge_affaires: form.charge_affaires || null,
            statut: form.statut,
            date_debut: form.date_debut || null,
            date_fin_prevue: form.date_fin_prevue || null,
            commentaire: form.commentaire || null,
          }),
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

      const affaireModifiee: Affaire = await response.json();

      setAffaires((actuelles) =>
        actuelles.map((affaire) =>
          affaire.id === affaireModifiee.id ? affaireModifiee : affaire
        )
      );
      setAffaireSelectionnee(affaireModifiee);
      setForm(versFormulaire(affaireModifiee));
      setModeEdition(false);
      setToast({
        type: "success",
        message: `${affaireModifiee.reference} mise à jour.`,
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
      <div className="breadcrumb">Exploitation / Affaires</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Chantiers et atelier</span>
          <h1>Affaires</h1>
          <p>
            Préparez les sorties de stock et suivez les consommations par affaire.
          </p>
        </div>

        <Button variant="secondary" onClick={ouvrirCreation}>
          <Plus size={18} />
          Nouvelle affaire
        </Button>
      </div>

      <section className={styles.summary}>
        <article>
          <BriefcaseBusiness size={20} />
          <div>
            <span>Affaires actives</span>
            <strong>
              {
                affaires.filter(
                  (affaire) =>
                    !["TERMINEE", "ANNULEE"].includes(affaire.statut)
                ).length
              }
            </strong>
          </div>
        </article>
        <article>
          <Building2 size={20} />
          <div>
            <span>Clients</span>
            <strong>
              {
                new Set(
                  affaires.map((affaire) => affaire.client).filter(Boolean)
                ).size
              }
            </strong>
          </div>
        </article>
        <article>
          <UserRound size={20} />
          <div>
            <span>Chargés d’affaires</span>
            <strong>
              {
                new Set(
                  affaires
                    .map((affaire) => affaire.charge_affaires)
                    .filter(Boolean)
                ).size
              }
            </strong>
          </div>
        </article>
        <article>
          <CalendarDays size={20} />
          <div>
            <span>En cours</span>
            <strong>
              {
                affaires.filter(
                  (affaire) => affaire.statut === "EN_COURS"
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
              placeholder="Référence, client, site ou chargé d’affaires"
              value={recherche}
              onChange={(event) => setRecherche(event.target.value)}
            />
          </label>

          <select
            value={filtreStatut}
            onChange={(event) => setFiltreStatut(event.target.value)}
          >
            <option value="">Tous les statuts</option>
            {statuts.map((statut) => (
              <option key={statut.value} value={statut.value}>
                {statut.label}
              </option>
            ))}
          </select>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Affaire</th>
                <th>Client</th>
                <th>Site / zone</th>
                <th>Chargé d’affaires</th>
                <th>Début</th>
                <th>Fin prévue</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {affairesFiltrees.map((affaire) => {
                const statut = statutAffaire(affaire.statut);

                return (
                  <tr
                    key={affaire.id}
                    className="clickable-row"
                    onClick={() => ouvrirAffaire(affaire)}
                  >
                    <td>
                      <div className={styles.affaireCell}>
                        <span className="reference-chip">
                          {affaire.code_externe || affaire.reference}
                        </span>
                        <strong>{affaire.nom}</strong>
                      </div>
                    </td>
                    <td>{affaire.client ?? "—"}</td>
                    <td>
                      <strong>{affaire.site ?? "—"}</strong>
                      {affaire.zone_intervention && (
                        <small className="table-subtext">
                          {affaire.zone_intervention}
                        </small>
                      )}
                    </td>
                    <td>{affaire.charge_affaires ?? "—"}</td>
                    <td>
                      {affaire.date_debut
                        ? new Intl.DateTimeFormat("fr-FR").format(
                            new Date(`${affaire.date_debut}T00:00:00`)
                          )
                        : "—"}
                    </td>
                    <td>
                      {affaire.date_fin_prevue
                        ? new Intl.DateTimeFormat("fr-FR").format(
                            new Date(`${affaire.date_fin_prevue}T00:00:00`)
                          )
                        : "—"}
                    </td>
                    <td>
                      <Badge tone={statut.tone}>{statut.label}</Badge>
                    </td>
                  </tr>
                );
              })}

              {affairesFiltrees.length === 0 && (
                <tr>
                  <td colSpan={7} className="empty-state">
                    <BriefcaseBusiness size={24} />
                    <strong>Aucune affaire</strong>
                    <span>Créez la première affaire chantier ou atelier.</span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <Drawer
        open={affaireSelectionnee !== null}
        title={
          affaireSelectionnee?.code_externe ||
          affaireSelectionnee?.reference ||
          ""
        }
        onClose={fermerDrawer}
      >
        {affaireSelectionnee && !modeEdition && (
          <div className={styles.detail}>
            <div className={styles.detailHeader}>
              <div>
                <h3>{affaireSelectionnee.nom}</h3>
                <p>
                  {affaireSelectionnee.client ?? "Client non renseigné"}
                </p>
              </div>
              <Badge tone={statutAffaire(affaireSelectionnee.statut).tone}>
                {statutAffaire(affaireSelectionnee.statut).label}
              </Badge>
            </div>

            <dl className="detail-grid">
              <div>
                <dt>Site</dt>
                <dd>{affaireSelectionnee.site ?? "—"}</dd>
              </div>
              <div>
                <dt>Zone</dt>
                <dd>{affaireSelectionnee.zone_intervention ?? "—"}</dd>
              </div>
              <div>
                <dt>Chargé d’affaires</dt>
                <dd>{affaireSelectionnee.charge_affaires ?? "—"}</dd>
              </div>
              <div>
                <dt>Référence interne</dt>
                <dd>{affaireSelectionnee.reference}</dd>
              </div>
              <div>
                <dt>Date de début</dt>
                <dd>{affaireSelectionnee.date_debut ?? "—"}</dd>
              </div>
              <div>
                <dt>Fin prévue</dt>
                <dd>{affaireSelectionnee.date_fin_prevue ?? "—"}</dd>
              </div>
            </dl>

            {affaireSelectionnee.commentaire && (
              <section className="drawer-section">
                <h4>Commentaire</h4>
                <div className="placeholder-panel">
                  {affaireSelectionnee.commentaire}
                </div>
              </section>
            )}

            <div className="drawer-actions">
              <Button
                variant="secondary"
                onClick={() => {
                  setForm(versFormulaire(affaireSelectionnee));
                  setModeEdition(true);
                }}
              >
                <Pencil size={17} />
                Modifier l’affaire
              </Button>
            </div>
          </div>
        )}

        {affaireSelectionnee && modeEdition && (
          <form onSubmit={modifier}>
            <div className="form-grid">
              <label className="field">
                <span>Code COREF / ERP</span>
                <input
                  maxLength={80}
                  value={form.code_externe}
                  onChange={(event) =>
                    setForm({ ...form, code_externe: event.target.value })
                  }
                />
              </label>

              <label className="field">
                <span>Statut *</span>
                <select
                  required
                  value={form.statut}
                  onChange={(event) =>
                    setForm({ ...form, statut: event.target.value })
                  }
                >
                  {statuts.map((statut) => (
                    <option key={statut.value} value={statut.value}>
                      {statut.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field field-wide">
                <span>Nom de l’affaire *</span>
                <input
                  required
                  maxLength={200}
                  value={form.nom}
                  onChange={(event) =>
                    setForm({ ...form, nom: event.target.value })
                  }
                />
              </label>

              <label className="field">
                <span>Client</span>
                <input
                  maxLength={180}
                  value={form.client}
                  onChange={(event) =>
                    setForm({ ...form, client: event.target.value })
                  }
                />
              </label>

              <label className="field">
                <span>Site</span>
                <input
                  maxLength={180}
                  value={form.site}
                  onChange={(event) =>
                    setForm({ ...form, site: event.target.value })
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
                <span>Date de début</span>
                <input
                  type="date"
                  value={form.date_debut}
                  onChange={(event) =>
                    setForm({ ...form, date_debut: event.target.value })
                  }
                />
              </label>

              <label className="field">
                <span>Date de fin prévue</span>
                <input
                  type="date"
                  value={form.date_fin_prevue}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      date_fin_prevue: event.target.value,
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

            <div className="modal-actions">
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  setForm(versFormulaire(affaireSelectionnee));
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
                <span className="eyebrow">Nouvelle affaire</span>
                <h2>Créer une affaire</h2>
                <p>
                  Elle pourra être sélectionnée lors des sorties de stock.
                </p>
              </div>
            </div>

            <form onSubmit={creer}>
              <div className="form-grid">
                <label className="field">
                  <span>Code COREF / ERP</span>
                  <input
                    maxLength={80}
                    placeholder="Ex. A26-145"
                    value={form.code_externe}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        code_externe: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Statut *</span>
                  <select
                    required
                    value={form.statut}
                    onChange={(event) =>
                      setForm({ ...form, statut: event.target.value })
                    }
                  >
                    {statuts.map((statut) => (
                      <option key={statut.value} value={statut.value}>
                        {statut.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field field-wide">
                  <span>Nom de l’affaire *</span>
                  <input
                    required
                    maxLength={200}
                    value={form.nom}
                    onChange={(event) =>
                      setForm({ ...form, nom: event.target.value })
                    }
                  />
                </label>

                <label className="field">
                  <span>Client</span>
                  <input
                    maxLength={180}
                    value={form.client}
                    onChange={(event) =>
                      setForm({ ...form, client: event.target.value })
                    }
                  />
                </label>

                <label className="field">
                  <span>Site</span>
                  <input
                    maxLength={180}
                    value={form.site}
                    onChange={(event) =>
                      setForm({ ...form, site: event.target.value })
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
                  <span>Date de début</span>
                  <input
                    type="date"
                    value={form.date_debut}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        date_debut: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Date de fin prévue</span>
                  <input
                    type="date"
                    value={form.date_fin_prevue}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        date_fin_prevue: event.target.value,
                      })
                    }
                  />
                </label>
              </div>

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
                  {enregistrement ? "Création…" : "Créer l’affaire"}
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
