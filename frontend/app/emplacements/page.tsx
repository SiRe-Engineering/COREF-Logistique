"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { ChevronRight, MapPin, Plus, Warehouse } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";

type Emplacement = {
  id: number;
  code: string;
  nom: string;
  type: string;
  parent_id: number | null;
  allee: string | null;
  rack: string | null;
  etage: number | null;
  case: string | null;
  actif: boolean;
  enfants: Emplacement[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialForm = {
  nom: "",
  type: "ZONE",
  parent_id: "",
  allee: "",
  rack: "",
  etage: "",
  case: "",
};

export default function EmplacementsPage() {
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [modalOuverte, setModalOuverte] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const response = await fetch(`${API_URL}/api/emplacements`);
      if (!response.ok) throw new Error();
      setEmplacements(await response.json());
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger les emplacements.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const optionsParents = useMemo(
    () => emplacements.flatMap((racine) => [racine, ...racine.enfants]),
    [emplacements]
  );

  async function creer(event: FormEvent) {
    event.preventDefault();

    try {
      const response = await fetch(`${API_URL}/api/emplacements`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nom: form.nom,
          type: form.type,
          parent_id: form.parent_id ? Number(form.parent_id) : null,
          allee: form.allee || null,
          rack: form.rack || null,
          etage: form.etage ? Number(form.etage) : null,
          case: form.case || null,
        }),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail ?? "Création impossible.");
      }

      setModalOuverte(false);
      setForm(initialForm);
      setToast({
        type: "success",
        message: "Emplacement créé.",
      });
      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error ? cause.message : "Création impossible.",
      });
    }
  }

  return (
    <div>
      <div className="breadcrumb">Référentiel / Emplacements</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Localisation</span>
          <h1>Emplacements</h1>
          <p>
            Structurez les zones, racks, étages et cases de stockage de COREF.
          </p>
        </div>

        <Button variant="secondary" onClick={() => setModalOuverte(true)}>
          <Plus size={18} />
          Nouvel emplacement
        </Button>
      </div>

      <section className="locations-grid">
        {emplacements.map((emplacement) => (
          <article className="location-card" key={emplacement.id}>
            <div className="location-card-header">
              <div className="location-icon">
                {emplacement.code === "RAC-MOU" ? (
                  <Warehouse size={20} />
                ) : (
                  <MapPin size={20} />
                )}
              </div>
              <div>
                <strong>{emplacement.nom}</strong>
                <span>{emplacement.code}</span>
              </div>
            </div>

            <div className="location-children">
              {emplacement.enfants.length === 0 ? (
                <span className="muted-text">Aucun sous-emplacement</span>
              ) : (
                emplacement.enfants.map((enfant) => (
                  <div className="location-child" key={enfant.id}>
                    <ChevronRight size={15} />
                    <span>{enfant.nom}</span>
                    <code>{enfant.code}</code>
                  </div>
                ))
              )}
            </div>
          </article>
        ))}
      </section>

      {modalOuverte && (
        <div className="modal-backdrop" onMouseDown={() => setModalOuverte(false)}>
          <section
            className="modal-card"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">Nouvelle localisation</span>
                <h2>Créer un emplacement</h2>
              </div>
            </div>

            <form onSubmit={creer}>
              <div className="form-grid">
                <label className="field field-wide">
                  <span>Nom *</span>
                  <input
                    required
                    value={form.nom}
                    onChange={(event) =>
                      setForm({ ...form, nom: event.target.value })
                    }
                    placeholder="Ex. Rack A1 — Étage 2 — Case B"
                  />
                </label>

                <label className="field">
                  <span>Type *</span>
                  <select
                    value={form.type}
                    onChange={(event) =>
                      setForm({ ...form, type: event.target.value })
                    }
                  >
                    <option value="ZONE">Zone</option>
                    <option value="RACK">Rack</option>
                    <option value="CASE_MOULE">Case de moule</option>
                    <option value="VEHICULE">Véhicule</option>
                    <option value="CHANTIER">Chantier</option>
                  </select>
                </label>

                <label className="field">
                  <span>Emplacement parent</span>
                  <select
                    value={form.parent_id}
                    onChange={(event) =>
                      setForm({ ...form, parent_id: event.target.value })
                    }
                  >
                    <option value="">Aucun</option>
                    {optionsParents.map((emplacement) => (
                      <option key={emplacement.id} value={emplacement.id}>
                        {emplacement.nom}
                      </option>
                    ))}
                  </select>
                </label>

                {form.type === "CASE_MOULE" && (
                  <>
                    <label className="field">
                      <span>Allée *</span>
                      <select
                        value={form.allee}
                        onChange={(event) =>
                          setForm({ ...form, allee: event.target.value })
                        }
                      >
                        <option value="">Sélectionner</option>
                        {["A", "B", "C", "D", "E"].map((valeur) => (
                          <option key={valeur}>{valeur}</option>
                        ))}
                      </select>
                    </label>

                    <label className="field">
                      <span>Rack *</span>
                      <select
                        value={form.rack}
                        onChange={(event) =>
                          setForm({ ...form, rack: event.target.value })
                        }
                      >
                        <option value="">Sélectionner</option>
                        {["1", "2", "3", "4"].map((valeur) => (
                          <option key={valeur}>{valeur}</option>
                        ))}
                      </select>
                    </label>

                    <label className="field">
                      <span>Étage *</span>
                      <select
                        value={form.etage}
                        onChange={(event) =>
                          setForm({ ...form, etage: event.target.value })
                        }
                      >
                        <option value="">Sélectionner</option>
                        {["1", "2", "3", "4"].map((valeur) => (
                          <option key={valeur}>{valeur}</option>
                        ))}
                      </select>
                    </label>

                    <label className="field">
                      <span>Case *</span>
                      <select
                        value={form.case}
                        onChange={(event) =>
                          setForm({ ...form, case: event.target.value })
                        }
                      >
                        <option value="">Sélectionner</option>
                        {["A", "B", "C", "D"].map((valeur) => (
                          <option key={valeur}>{valeur}</option>
                        ))}
                      </select>
                    </label>
                  </>
                )}
              </div>

              <div className="modal-actions">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setModalOuverte(false)}
                >
                  Annuler
                </Button>
                <Button type="submit">Créer l’emplacement</Button>
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
