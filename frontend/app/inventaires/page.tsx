"use client";

import { FormEvent, useEffect, useState } from "react";
import {
  CheckCircle2,
  ClipboardCheck,
  Plus,
  Scale,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Toast } from "@/components/ui/Toast";
import styles from "./page.module.css";

type Emplacement = {
  id: number;
  code: string;
  nom: string;
};

type Ligne = {
  id: number;
  article_id: number;
  lot_id: number | null;
  quantite_theorique: string;
  quantite_comptee: string | null;
  ecart: string | null;
  commentaire: string | null;
  article: {
    reference: string;
    designation: string;
    unite: string;
  };
  lot: {
    numero_lot_fournisseur: string;
  } | null;
};

type Inventaire = {
  id: number;
  reference: string;
  nom: string;
  statut: string;
  operateur: string | null;
  date_creation: string;
  date_validation: string | null;
  emplacement: Emplacement;
  lignes: Ligne[];
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function InventairesPage() {
  const [inventaires, setInventaires] = useState<Inventaire[]>([]);
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [selection, setSelection] = useState<Inventaire | null>(null);
  const [modalOuverte, setModalOuverte] = useState(false);
  const [form, setForm] = useState({
    nom: "",
    emplacement_id: "",
    operateur: "Utilisateur local",
  });
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const [inventairesResponse, emplacementsResponse] = await Promise.all([
        fetch(`${API_URL}/api/inventaires`),
        fetch(`${API_URL}/api/emplacements?racines_uniquement=false`),
      ]);

      if (!inventairesResponse.ok || !emplacementsResponse.ok) {
        throw new Error();
      }

      setInventaires(await inventairesResponse.json());
      setEmplacements(await emplacementsResponse.json());
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger les inventaires.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  async function creer(event: FormEvent) {
    event.preventDefault();

    try {
      const response = await fetch(`${API_URL}/api/inventaires`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nom: form.nom,
          emplacement_id: Number(form.emplacement_id),
          operateur: form.operateur || null,
        }),
      });

      if (!response.ok) throw new Error("Création impossible.");

      const inventaire = await response.json();
      setModalOuverte(false);
      setForm({
        nom: "",
        emplacement_id: "",
        operateur: "Utilisateur local",
      });
      setSelection(inventaire);
      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error ? cause.message : "Création impossible.",
      });
    }
  }

  async function saisir(
    inventaireId: number,
    ligneId: number,
    valeur: string
  ) {
    const response = await fetch(
      `${API_URL}/api/inventaires/${inventaireId}/lignes/${ligneId}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quantite_comptee: Number(valeur),
        }),
      }
    );

    if (!response.ok) {
      setToast({
        type: "error",
        message: "Saisie impossible.",
      });
      return;
    }

    const inventaire = await response.json();
    setSelection(inventaire);
    setInventaires((actuels) =>
      actuels.map((element) =>
        element.id === inventaire.id ? inventaire : element
      )
    );
  }

  async function valider() {
    if (!selection) return;

    try {
      const response = await fetch(
        `${API_URL}/api/inventaires/${selection.id}/valider`,
        { method: "POST" }
      );

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail ?? "Validation impossible.");
      }

      const inventaire = await response.json();
      setSelection(inventaire);
      await charger();
      setToast({
        type: "success",
        message: `${inventaire.reference} validé.`,
      });
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Validation impossible.",
      });
    }
  }

  return (
    <div>
      <div className="breadcrumb">Exploitation / Inventaires</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Comptage physique</span>
          <h1>Inventaires</h1>
          <p>
            Comptez le stock par emplacement et régularisez les écarts.
          </p>
        </div>

        <Button variant="secondary" onClick={() => setModalOuverte(true)}>
          <Plus size={18} />
          Nouvel inventaire
        </Button>
      </div>

      <section className={styles.cards}>
        {inventaires.map((inventaire) => {
          const saisies = inventaire.lignes.filter(
            (ligne) => ligne.quantite_comptee !== null
          ).length;

          return (
            <article
              key={inventaire.id}
              className={styles.card}
              onClick={() => setSelection(inventaire)}
            >
              <div className={styles.cardHeader}>
                <ClipboardCheck size={20} />
                <div>
                  <strong>{inventaire.nom}</strong>
                  <span>{inventaire.reference}</span>
                </div>
              </div>
              <p>{inventaire.emplacement.nom}</p>
              <div className={styles.progress}>
                <span>
                  {saisies} / {inventaire.lignes.length} lignes
                </span>
                <strong>{inventaire.statut}</strong>
              </div>
            </article>
          );
        })}
      </section>

      <Drawer
        open={selection !== null}
        title={selection?.reference ?? ""}
        onClose={() => setSelection(null)}
      >
        {selection && (
          <div>
            <div className={styles.inventoryHeader}>
              <div>
                <h3>{selection.nom}</h3>
                <p>{selection.emplacement.nom}</p>
              </div>
              <strong>{selection.statut}</strong>
            </div>

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
                  </div>

                  <div className={styles.quantities}>
                    <label>
                      <span>Théorique</span>
                      <strong>
                        {Number(ligne.quantite_theorique).toLocaleString("fr-FR")}{" "}
                        {ligne.article.unite}
                      </strong>
                    </label>

                    <label>
                      <span>Compté</span>
                      <input
                        type="number"
                        min="0"
                        step="0.001"
                        disabled={selection.statut !== "EN_COURS"}
                        defaultValue={ligne.quantite_comptee ?? ""}
                        onBlur={(event) => {
                          if (event.target.value !== "") {
                            saisir(
                              selection.id,
                              ligne.id,
                              event.target.value
                            );
                          }
                        }}
                      />
                    </label>

                    <label>
                      <span>Écart</span>
                      <strong>
                        {ligne.ecart === null
                          ? "—"
                          : Number(ligne.ecart).toLocaleString("fr-FR")}
                      </strong>
                    </label>
                  </div>
                </div>
              ))}
            </div>

            {selection.statut === "EN_COURS" && (
              <div className="drawer-actions">
                <Button onClick={valider}>
                  <CheckCircle2 size={17} />
                  Valider l’inventaire
                </Button>
              </div>
            )}
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
                <span className="eyebrow">Nouveau comptage</span>
                <h2>Créer un inventaire</h2>
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
                    placeholder="Ex. Inventaire magasin août 2026"
                  />
                </label>

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
                  <span>Opérateur</span>
                  <input
                    value={form.operateur}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        operateur: event.target.value,
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
                <Button type="submit">
                  <Scale size={17} />
                  Démarrer le comptage
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
