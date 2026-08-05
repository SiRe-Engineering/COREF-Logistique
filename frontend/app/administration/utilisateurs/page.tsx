"use client";

import { FormEvent, useEffect, useState } from "react";
import { Plus, Users } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import { Button } from "@/components/ui/Button";
import { entetesAuthentifiees } from "@/lib/auth";

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

export default function UtilisateursPage() {
  const { utilisateur } = useAuth();
  const [utilisateurs, setUtilisateurs] = useState<Utilisateur[]>([]);
  const [modalOuverte, setModalOuverte] = useState(false);
  const [erreur, setErreur] = useState("");
  const [form, setForm] = useState({
    prenom: "",
    nom: "",
    email: "",
    mot_de_passe: "",
    role: "UTILISATEUR_STANDARD",
    type_compte: "METIER",
    entreprise: "COREF",
    fonction: "",
    nom_complet: "",
  });

  const administrateurTechnique =
    utilisateur.role === "ADMINISTRATEUR_TECHNIQUE";
  const peutGerer = [
    "ADMINISTRATEUR_TECHNIQUE",
    "ADMINISTRATEUR_COREF",
  ].includes(utilisateur.role);

  async function charger() {
    const response = await fetch(`${API_URL}/api/utilisateurs`, {
      headers: entetesAuthentifiees(),
    });
    if (response.ok) setUtilisateurs(await response.json());
  }

  useEffect(() => {
    if (peutGerer) charger();
  }, [peutGerer]);

  async function creer(event: FormEvent) {
    event.preventDefault();
    setErreur("");

    const response = await fetch(`${API_URL}/api/utilisateurs`, {
      method: "POST",
      headers: entetesAuthentifiees({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({
        ...form,
        prenom: form.type_compte === "METIER" ? form.prenom : null,
        nom: form.type_compte === "METIER" ? form.nom : null,
        nom_complet:
          form.type_compte === "TECHNIQUE"
            ? form.nom_complet
            : null,
        fonction: form.fonction || null,
      }),
    });

    if (!response.ok) {
      const detail = await response.json().catch(() => null);
      setErreur(
        typeof detail?.detail === "string"
          ? detail.detail
          : "Création impossible."
      );
      return;
    }

    setModalOuverte(false);
    setForm({
      prenom: "",
      nom: "",
      email: "",
      mot_de_passe: "",
      role: "UTILISATEUR_STANDARD",
      type_compte: "METIER",
      entreprise: "COREF",
      fonction: "",
      nom_complet: "",
    });
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
            Les comptes techniques SiRe Engineering sont séparés des
            utilisateurs métier COREF.
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() => setModalOuverte(true)}
        >
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
              </tr>
            </thead>
            <tbody>
              {utilisateurs.map((element) => (
                <tr key={element.id}>
                  <td><strong>{element.nom_complet}</strong></td>
                  <td>{element.entreprise}</td>
                  <td>{element.email}</td>
                  <td>{element.fonction ?? "—"}</td>
                  <td>
                    {element.type_compte === "TECHNIQUE"
                      ? "Technique"
                      : "Métier"}
                  </td>
                  <td>{element.role.replaceAll("_", " ")}</td>
                  <td>{element.actif ? "Actif" : "Inactif"}</td>
                </tr>
              ))}
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
                <span className="eyebrow">Nouveau compte</span>
                <h2>Créer un utilisateur</h2>
              </div>
            </div>

            <form onSubmit={creer}>
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
                  <span>Mot de passe temporaire *</span>
                  <input
                    required
                    minLength={10}
                    type="password"
                    value={form.mot_de_passe}
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
              </div>

              {erreur && (
                <div style={{ color: "#b42318", marginTop: 12 }}>
                  {erreur}
                </div>
              )}

              <div className="modal-actions">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setModalOuverte(false)}
                >
                  Annuler
                </Button>
                <Button type="submit">Créer le compte</Button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
