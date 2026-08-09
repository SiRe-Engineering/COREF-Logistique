"use client";

import { apiFetch } from "@/lib/api";

import { FormEvent, useEffect, useState } from "react";
import { Pencil, Plus, Trash2, Users } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import { Button } from "@/components/ui/Button";
import { entetesAuthentifiees } from "@/lib/auth";
import styles from "./page.module.css";

type Utilisateur = {
  id: number;
  nom_complet: string;
  prenom: string | null;
  nom: string | null;
  email: string;
  role: string;
  type_compte: string;
  entreprise: string;
  fonction: string | null;
  actif: boolean;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const rolesMetier = [
  "ADMINISTRATEUR_COREF",
  "RESPONSABLE_LOGISTIQUE",
  "RESPONSABLE_PRODUCTION",
  "CHARGE_AFFAIRES",
  "UTILISATEUR_STANDARD",
  "CONSULTATION",
];

const formulaireVide = {
  prenom: "",
  nom: "",
  email: "",
  mot_de_passe: "",
  role: "UTILISATEUR_STANDARD",
  type_compte: "METIER",
  entreprise: "COREF",
  fonction: "",
  nom_complet: "",
  actif: true,
};

function messageErreur(detail: unknown) {
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((element) =>
        typeof element === "object" &&
        element !== null &&
        "msg" in element
          ? String(element.msg)
          : ""
      )
      .filter(Boolean)
      .join(" · ");
  }

  return "Opération impossible.";
}

export default function UtilisateursPage() {
  const { utilisateur } = useAuth();
  const [utilisateurs, setUtilisateurs] = useState<Utilisateur[]>([]);
  const [modalOuverte, setModalOuverte] = useState(false);
  const [utilisateurEdite, setUtilisateurEdite] =
    useState<Utilisateur | null>(null);
  const [erreur, setErreur] = useState("");
  const [form, setForm] = useState(formulaireVide);

  const administrateurTechnique =
    utilisateur.role === "ADMINISTRATEUR_TECHNIQUE";
  const peutGerer = [
    "ADMINISTRATEUR_TECHNIQUE",
    "ADMINISTRATEUR_COREF",
  ].includes(utilisateur.role);

  async function charger() {
    const response = await apiFetch(`${API_URL}/api/utilisateurs`, {
      headers: entetesAuthentifiees(),
    });

    if (response.ok) {
      setUtilisateurs(await response.json());
    }
  }

  useEffect(() => {
    if (peutGerer) charger();
  }, [peutGerer]);

  function ouvrirCreation() {
    setUtilisateurEdite(null);
    setForm(formulaireVide);
    setErreur("");
    setModalOuverte(true);
  }

  function ouvrirEdition(element: Utilisateur) {
    setUtilisateurEdite(element);
    setForm({
      prenom: element.prenom ?? "",
      nom: element.nom ?? "",
      email: element.email,
      mot_de_passe: "",
      role: element.role,
      type_compte: element.type_compte,
      entreprise: element.entreprise,
      fonction: element.fonction ?? "",
      nom_complet: element.nom_complet,
      actif: element.actif,
    });
    setErreur("");
    setModalOuverte(true);
  }

  async function enregistrer(event: FormEvent) {
    event.preventDefault();
    setErreur("");

    const edition = utilisateurEdite !== null;
    const response = await apiFetch(
      edition
        ? `${API_URL}/api/utilisateurs/${utilisateurEdite.id}`
        : `${API_URL}/api/utilisateurs`,
      {
        method: edition ? "PATCH" : "POST",
        headers: entetesAuthentifiees({
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({
          prenom: form.type_compte === "METIER" ? form.prenom : null,
          nom: form.type_compte === "METIER" ? form.nom : null,
          nom_complet:
            form.type_compte === "TECHNIQUE"
              ? form.nom_complet
              : null,
          email: form.email,
          ...(form.mot_de_passe
            ? { mot_de_passe: form.mot_de_passe }
            : {}),
          role: form.role,
          type_compte: form.type_compte,
          entreprise: form.entreprise,
          fonction: form.fonction || null,
          ...(edition ? { actif: form.actif } : {}),
        }),
      }
    );

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      setErreur(messageErreur(data?.detail));
      return;
    }

    setModalOuverte(false);
    setUtilisateurEdite(null);
    setForm(formulaireVide);
    await charger();
  }

  async function supprimer(element: Utilisateur) {
    if (
      !window.confirm(
        `Supprimer le compte de ${element.nom_complet} ?\n\n` +
          "Le compte sera désactivé et ses sessions seront immédiatement révoquées. " +
          "Son historique métier sera conservé."
      )
    ) {
      return;
    }

    const response = await apiFetch(
      `${API_URL}/api/utilisateurs/${element.id}`,
      {
        method: "DELETE",
        headers: entetesAuthentifiees(),
      }
    );

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      window.alert(messageErreur(data?.detail));
      return;
    }

    await charger();
  }

  if (!peutGerer) {
    return (
      <div className="empty-state">
        <Users size={28} />
        <strong>Accès réservé aux administrateurs</strong>
      </div>
    );
  }

  return (
    <div>
      <div className="breadcrumb">Administration / Utilisateurs</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Administration</span>
          <h1>Utilisateurs</h1>
          <p>
            Seuls les administrateurs peuvent créer, modifier ou supprimer
            les comptes.
          </p>
        </div>

        <Button variant="secondary" onClick={ouvrirCreation}>
          <Plus size={18} />
          Nouvel utilisateur
        </Button>
      </div>

      <section className="content-card">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Utilisateur</th>
                <th>Entreprise</th>
                <th>E-mail</th>
                <th>Fonction</th>
                <th>Type</th>
                <th>Rôle</th>
                <th>Statut</th>
                <th aria-label="Actions" />
              </tr>
            </thead>

            <tbody>
              {utilisateurs.map((element) => {
                const compteCourant = element.id === utilisateur.id;

                return (
                  <tr
                    key={element.id}
                    className={!element.actif ? styles.inactiveRow : ""}
                  >
                    <td>
                      <strong>{element.nom_complet}</strong>
                      {compteCourant && (
                        <small className="table-subtext">
                          Votre compte
                        </small>
                      )}
                    </td>
                    <td>{element.entreprise}</td>
                    <td>{element.email}</td>
                    <td>{element.fonction ?? "—"}</td>
                    <td>
                      {element.type_compte === "TECHNIQUE"
                        ? "Technique"
                        : "Métier"}
                    </td>
                    <td>{element.role.replaceAll("_", " ")}</td>
                    <td>
                      <span
                        className={
                          element.actif
                            ? styles.activeStatus
                            : styles.inactiveStatus
                        }
                      >
                        {element.actif ? "Actif" : "Supprimé"}
                      </span>
                    </td>
                    <td>
                      {!compteCourant && (
                        <div className={styles.actions}>
                          <button
                            type="button"
                            title="Modifier l’utilisateur"
                            onClick={() => ouvrirEdition(element)}
                          >
                            <Pencil size={16} />
                          </button>

                          {element.actif && (
                            <button
                              type="button"
                              title="Supprimer l’utilisateur"
                              className={styles.deleteButton}
                              onClick={() => supprimer(element)}
                            >
                              <Trash2 size={16} />
                            </button>
                          )}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
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
                <span className="eyebrow">
                  {utilisateurEdite
                    ? "Modification du compte"
                    : "Nouveau compte"}
                </span>
                <h2>
                  {utilisateurEdite
                    ? `Modifier ${utilisateurEdite.nom_complet}`
                    : "Créer un utilisateur"}
                </h2>
              </div>
            </div>

            <form onSubmit={enregistrer}>
              <div className="form-grid">
                {administrateurTechnique && (
                  <label className="field field-wide">
                    <span>Type de compte *</span>
                    <select
                      value={form.type_compte}
                      onChange={(event) => {
                        const type = event.target.value;
                        setForm({
                          ...form,
                          type_compte: type,
                          entreprise:
                            type === "TECHNIQUE"
                              ? "SiRe Engineering"
                              : "COREF",
                          role:
                            type === "TECHNIQUE"
                              ? "ADMINISTRATEUR_TECHNIQUE"
                              : "UTILISATEUR_STANDARD",
                        });
                      }}
                    >
                      <option value="METIER">Métier COREF</option>
                      <option value="TECHNIQUE">
                        Technique SiRe Engineering
                      </option>
                    </select>
                  </label>
                )}

                {form.type_compte === "METIER" ? (
                  <>
                    <label className="field">
                      <span>Prénom *</span>
                      <input
                        required
                        value={form.prenom}
                        onChange={(event) =>
                          setForm({
                            ...form,
                            prenom: event.target.value,
                          })
                        }
                      />
                    </label>

                    <label className="field">
                      <span>Nom *</span>
                      <input
                        required
                        value={form.nom}
                        onChange={(event) =>
                          setForm({
                            ...form,
                            nom: event.target.value,
                          })
                        }
                      />
                    </label>
                  </>
                ) : (
                  <label className="field field-wide">
                    <span>Nom affiché *</span>
                    <input
                      required
                      value={form.nom_complet}
                      onChange={(event) =>
                        setForm({
                          ...form,
                          nom_complet: event.target.value,
                        })
                      }
                    />
                  </label>
                )}

                <label className="field field-wide">
                  <span>E-mail *</span>
                  <input
                    required
                    type="email"
                    value={form.email}
                    onChange={(event) =>
                      setForm({ ...form, email: event.target.value })
                    }
                  />
                </label>

                <label className="field">
                  <span>Entreprise *</span>
                  <input
                    required
                    disabled={!administrateurTechnique}
                    value={form.entreprise}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        entreprise: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Fonction</span>
                  <input
                    value={form.fonction}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        fonction: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>
                    {utilisateurEdite
                      ? "Nouveau mot de passe"
                      : "Mot de passe temporaire *"}
                  </span>
                  <input
                    required={!utilisateurEdite}
                    minLength={10}
                    type="password"
                    value={form.mot_de_passe}
                    placeholder={
                      utilisateurEdite
                        ? "Laisser vide pour ne pas modifier"
                        : ""
                    }
                    onChange={(event) =>
                      setForm({
                        ...form,
                        mot_de_passe: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="field">
                  <span>Rôle *</span>
                  <select
                    value={form.role}
                    disabled={form.type_compte === "TECHNIQUE"}
                    onChange={(event) =>
                      setForm({ ...form, role: event.target.value })
                    }
                  >
                    {(form.type_compte === "TECHNIQUE"
                      ? ["ADMINISTRATEUR_TECHNIQUE"]
                      : rolesMetier
                    ).map((role) => (
                      <option key={role} value={role}>
                        {role.replaceAll("_", " ")}
                      </option>
                    ))}
                  </select>
                </label>

                {utilisateurEdite && (
                  <label className="field field-wide">
                    <span>Statut du compte</span>
                    <select
                      value={form.actif ? "ACTIF" : "INACTIF"}
                      onChange={(event) =>
                        setForm({
                          ...form,
                          actif: event.target.value === "ACTIF",
                        })
                      }
                    >
                      <option value="ACTIF">Actif</option>
                      <option value="INACTIF">
                        Supprimé / désactivé
                      </option>
                    </select>
                  </label>
                )}
              </div>

              {erreur && (
                <div className={styles.error}>{erreur}</div>
              )}

              <div className="modal-actions">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setModalOuverte(false)}
                >
                  Annuler
                </Button>

                <Button type="submit">
                  {utilisateurEdite
                    ? "Enregistrer les modifications"
                    : "Créer le compte"}
                </Button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
