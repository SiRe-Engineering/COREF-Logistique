"use client";

import { entetesAuthentifiees } from "@/lib/auth";
import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  ClipboardCheck,
  Plus,
  Search,
  Scale,
} from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Toast } from "@/components/ui/Toast";
import styles from "./page.module.css";


type Emplacement = {
  id: number;
  code: string;
  nom: string;
};

type Famille = {
  id: number;
  code: string;
  nom: string;
};

type Ligne = {
  id: number;
  emplacement_id: number;
  article_id: number;
  lot_id: number | null;
  quantite_theorique: string;
  quantite_comptee: string | null;
  ecart: string | null;
  pourcentage_ecart: string | null;
  commentaire: string | null;
  emplacement: Emplacement;
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
  type: string;
  emplacement_id: number | null;
  famille_id: number | null;
  statut: string;
  operateur: string | null;
  valide_par: string | null;
  date_creation: string;
  date_validation: string | null;
  emplacement: Emplacement | null;
  famille: Famille | null;
  lignes: Ligne[];
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const initialForm = {
  type: "EMPLACEMENT",
  emplacement_id: "",
  famille_id: "",
  commentaire: "",
};

function libelleType(type: string) {
  if (type === "GENERAL") return "Inventaire général";
  if (type === "FAMILLE") return "Par famille";
  return "Par emplacement";
}

function libellePerimetre(inventaire: Inventaire) {
  if (inventaire.emplacement) {
    return `${inventaire.emplacement.code} — ${inventaire.emplacement.nom}`;
  }
  if (inventaire.famille) {
    return `${inventaire.famille.code} — ${inventaire.famille.nom}`;
  }
  return "Tous les emplacements";
}

export default function InventairesPage() {
  const { utilisateur } = useAuth();
  const [inventaires, setInventaires] = useState<Inventaire[]>([]);
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [familles, setFamilles] = useState<Famille[]>([]);
  const [selection, setSelection] = useState<Inventaire | null>(null);
  const [modalOuverte, setModalOuverte] = useState(false);
  const [recherche, setRecherche] = useState("");
  const [filtreStatut, setFiltreStatut] = useState("");
  const [form, setForm] = useState(initialForm);
  const [sauvegarde, setSauvegarde] = useState<number | null>(null);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  async function charger() {
    try {
      const [inventairesResponse, emplacementsResponse, famillesResponse] =
        await Promise.all([
          fetch(`${API_URL}/api/inventaires`, {
            headers: entetesAuthentifiees(),
          }),
          fetch(
            `${API_URL}/api/emplacements?racines_uniquement=false`
          ),
          fetch(`${API_URL}/api/familles`),
        ]);

      if (
        !inventairesResponse.ok ||
        !emplacementsResponse.ok ||
        !famillesResponse.ok
      ) {
        throw new Error();
      }

      setInventaires(await inventairesResponse.json());
      setEmplacements(await emplacementsResponse.json());
      setFamilles(await famillesResponse.json());
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


  const apercuNom = useMemo(() => {
    const date = new Intl.DateTimeFormat("fr-CA").format(
      new Date()
    );

    if (form.type === "EMPLACEMENT") {
      const emplacement = emplacements.find(
        (item) => item.id === Number(form.emplacement_id)
      );
      return emplacement
        ? `${date} - Emplacement - ${emplacement.nom}`
        : `${date} - Emplacement - …`;
    }

    if (form.type === "FAMILLE") {
      const famille = familles.find(
        (item) => item.id === Number(form.famille_id)
      );
      return famille
        ? `${date} - Famille - ${famille.nom}`
        : `${date} - Famille - …`;
    }

    return `${date} - Général`;
  }, [
    form.type,
    form.emplacement_id,
    form.famille_id,
    emplacements,
    familles,
  ]);

  const inventairesFiltres = useMemo(() => {
    const terme = recherche.trim().toLowerCase();
    return inventaires.filter((inventaire) => {
      const correspondRecherche =
        !terme ||
        inventaire.reference.toLowerCase().includes(terme) ||
        inventaire.nom.toLowerCase().includes(terme) ||
        libellePerimetre(inventaire).toLowerCase().includes(terme);

      const correspondStatut =
        !filtreStatut || inventaire.statut === filtreStatut;

      return correspondRecherche && correspondStatut;
    });
  }, [inventaires, recherche, filtreStatut]);

  async function creer(event: FormEvent) {
    event.preventDefault();

    try {
      const response = await fetch(`${API_URL}/api/inventaires`, {
        method: "POST",
        headers: entetesAuthentifiees({
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({
          type: form.type,
          emplacement_id:
            form.type === "EMPLACEMENT"
              ? Number(form.emplacement_id)
              : null,
          famille_id:
            form.type === "FAMILLE"
              ? Number(form.famille_id)
              : null,
          operateur: utilisateur?.nom_complet ?? null,
          commentaire: form.commentaire.trim() || null,
        }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : "Création impossible."
        );
      }

      setModalOuverte(false);
      setForm(initialForm);
      setSelection(data);
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

  async function saisir(
    inventaireId: number,
    ligneId: number,
    quantite: string,
    commentaire: string
  ) {
    const valeur = Number(quantite.replace(",", "."));
    if (!Number.isFinite(valeur) || valeur < 0) {
      setToast({
        type: "error",
        message: "La quantité comptée est invalide.",
      });
      return;
    }

    setSauvegarde(ligneId);
    try {
      const response = await fetch(
        `${API_URL}/api/inventaires/${inventaireId}/lignes/${ligneId}`,
        {
          method: "PATCH",
          headers: entetesAuthentifiees({
            "Content-Type": "application/json",
          }),
          body: JSON.stringify({
            quantite_comptee: valeur,
            commentaire: commentaire.trim() || null,
          }),
        }
      );

      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : "Saisie impossible."
        );
      }

      setSelection(data);
      setInventaires((actuels) =>
        actuels.map((element) =>
          element.id === data.id ? data : element
        )
      );
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error ? cause.message : "Saisie impossible.",
      });
    } finally {
      setSauvegarde(null);
    }
  }

  async function valider() {
    if (!selection) return;

    const nonCompte = selection.lignes.filter(
      (ligne) => ligne.quantite_comptee === null
    ).length;
    if (nonCompte > 0) {
      setToast({
        type: "error",
        message: `${nonCompte} ligne(s) restent à compter.`,
      });
      return;
    }

    const ecarts = selection.lignes.filter(
      (ligne) => Number(ligne.ecart || 0) !== 0
    ).length;

    if (
      !window.confirm(
        `Valider ${selection.reference} ?\n\n` +
          `${ecarts} ligne(s) d’écart généreront des mouvements ` +
          "d’ajustement."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/inventaires/${selection.id}/valider`,
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
            : "Validation impossible."
        );
      }

      setSelection(data);
      await charger();
      setToast({
        type: "success",
        message: `${data.reference} validé et stocks régularisés.`,
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

  const comptees = selection
    ? selection.lignes.filter(
        (ligne) => ligne.quantite_comptee !== null
      ).length
    : 0;
  const ecarts = selection
    ? selection.lignes.filter(
        (ligne) => Number(ligne.ecart || 0) !== 0
      ).length
    : 0;

  return (
    <div>
      <div className="breadcrumb">Exploitation / Inventaires</div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Comptage physique</span>
          <h1>Inventaires</h1>
          <p>
            Les stocks ne sont modifiés qu’après validation responsable.
          </p>
        </div>

        <Button
          variant="secondary"
          onClick={() => setModalOuverte(true)}
        >
          <Plus size={18} />
          Nouvel inventaire
        </Button>
      </div>

      <section className={styles.toolbar}>
        <label className="search-field">
          <Search size={17} />
          <input
            type="search"
            value={recherche}
            placeholder="Référence, nom ou périmètre"
            onChange={(event) => setRecherche(event.target.value)}
          />
        </label>
        <select
          value={filtreStatut}
          onChange={(event) => setFiltreStatut(event.target.value)}
        >
          <option value="">Tous les statuts</option>
          <option value="EN_COURS">En cours</option>
          <option value="VALIDE">Validé</option>
        </select>
      </section>

      <section className={styles.cards}>
        {inventairesFiltres.map((inventaire) => {
          const saisies = inventaire.lignes.filter(
            (ligne) => ligne.quantite_comptee !== null
          ).length;
          const anomalies = inventaire.lignes.filter(
            (ligne) => Number(ligne.ecart || 0) !== 0
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
              <p>{libellePerimetre(inventaire)}</p>
              <small>{libelleType(inventaire.type)}</small>
              <div className={styles.progress}>
                <span>
                  {saisies} / {inventaire.lignes.length} comptées
                </span>
                <strong>{inventaire.statut.replace("_", " ")}</strong>
              </div>
              <div className={styles.cardFooter}>
                <span>{anomalies} écart(s)</span>
              </div>
            </article>
          );
        })}

        {inventairesFiltres.length === 0 && (
          <div className={styles.empty}>
            Aucun inventaire ne correspond aux filtres.
          </div>
        )}
      </section>

      <Drawer
        open={selection !== null}
        title={selection?.reference ?? ""}
        size="workspace"
        onClose={() => setSelection(null)}
      >
        {selection && (
          <div className={styles.workspace}>
            <div className={styles.inventoryHeader}>
              <div>
                <h3>{selection.nom}</h3>
                <p>{libellePerimetre(selection)}</p>
              </div>
              <strong>{selection.statut.replace("_", " ")}</strong>
            </div>

            <section className={styles.kpis}>
              <div>
                <span>Lignes comptées</span>
                <strong>{comptees} / {selection.lignes.length}</strong>
              </div>
              <div>
                <span>Écarts</span>
                <strong>{ecarts}</strong>
              </div>
              <div>
                <span>Opérateur</span>
                <strong>{selection.operateur ?? "—"}</strong>
              </div>
              <div>
                <span>Validé par</span>
                <strong>{selection.valide_par ?? "—"}</strong>
              </div>
            </section>

            <div className={styles.lines}>
              {selection.lignes.map((ligne) => (
                <LigneComptage
                  key={ligne.id}
                  ligne={ligne}
                  editable={selection.statut === "EN_COURS"}
                  sauvegarde={sauvegarde === ligne.id}
                  onSave={(quantite, commentaire) =>
                    saisir(
                      selection.id,
                      ligne.id,
                      quantite,
                      commentaire
                    )
                  }
                />
              ))}
            </div>

            {selection.statut === "EN_COURS" && (
              <div className="drawer-actions">
                <Button onClick={valider}>
                  <CheckCircle2 size={17} />
                  Valider et régulariser
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
              <div className={styles.namePreview}>
                <span>Nom généré automatiquement</span>
                <strong>{apercuNom}</strong>
              </div>

              <div className="form-grid">
                <label className="field">
                  <span>Type *</span>
                  <select
                    value={form.type}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        type: event.target.value,
                        emplacement_id: "",
                        famille_id: "",
                      })
                    }
                  >
                    <option value="EMPLACEMENT">Par emplacement</option>
                    <option value="FAMILLE">Par famille</option>
                    <option value="GENERAL">Inventaire général</option>
                  </select>
                </label>

                {form.type === "EMPLACEMENT" && (
                  <label className="field">
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
                        <option
                          key={emplacement.id}
                          value={emplacement.id}
                        >
                          {emplacement.code} — {emplacement.nom}
                        </option>
                      ))}
                    </select>
                  </label>
                )}

                {form.type === "FAMILLE" && (
                  <label className="field">
                    <span>Famille *</span>
                    <select
                      required
                      value={form.famille_id}
                      onChange={(event) =>
                        setForm({
                          ...form,
                          famille_id: event.target.value,
                        })
                      }
                    >
                      <option value="">Sélectionner</option>
                      {familles.map((famille) => (
                        <option key={famille.id} value={famille.id}>
                          {famille.code} — {famille.nom}
                        </option>
                      ))}
                    </select>
                  </label>
                )}

                <label className="field field-wide">
                  <span>Commentaire</span>
                  <input
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

function LigneComptage({
  ligne,
  editable,
  sauvegarde,
  onSave,
}: {
  ligne: Ligne;
  editable: boolean;
  sauvegarde: boolean;
  onSave: (quantite: string, commentaire: string) => void;
}) {
  const [quantite, setQuantite] = useState(
    ligne.quantite_comptee ?? ""
  );
  const [commentaire, setCommentaire] = useState(
    ligne.commentaire ?? ""
  );

  useEffect(() => {
    setQuantite(ligne.quantite_comptee ?? "");
    setCommentaire(ligne.commentaire ?? "");
  }, [ligne.quantite_comptee, ligne.commentaire]);

  const ecart =
    quantite === ""
      ? null
      : Number(quantite.replace(",", ".")) -
        Number(ligne.quantite_theorique);

  return (
    <article className={styles.line}>
      <div className={styles.lineIdentity}>
        <strong>{ligne.article.designation}</strong>
        <span>{ligne.article.reference}</span>
        <small>
          {ligne.emplacement.code} — {ligne.emplacement.nom}
        </small>
        {ligne.lot && (
          <small>Lot {ligne.lot.numero_lot_fournisseur}</small>
        )}
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
            inputMode="decimal"
            disabled={!editable}
            value={quantite}
            onChange={(event) => setQuantite(event.target.value)}
            placeholder="0"
          />
        </label>

        <label>
          <span>Écart</span>
          <strong className={
            ecart === null
              ? ""
              : ecart === 0
                ? styles.zero
                : ecart > 0
                  ? styles.positive
                  : styles.negative
          }>
            {ecart === null
              ? "—"
              : ecart.toLocaleString("fr-FR")}
          </strong>
        </label>

        <label className={styles.comment}>
          <span>Commentaire</span>
          <input
            disabled={!editable}
            value={commentaire}
            onChange={(event) => setCommentaire(event.target.value)}
            placeholder="Observation ou cause de l’écart"
          />
        </label>

        {editable && (
          <Button
            type="button"
            variant="secondary"
            disabled={quantite === "" || sauvegarde}
            onClick={() => onSave(quantite, commentaire)}
          >
            {sauvegarde ? "Sauvegarde…" : "Enregistrer"}
          </Button>
        )}
      </div>
    </article>
  );
}
