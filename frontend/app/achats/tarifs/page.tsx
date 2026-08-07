"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  BadgeEuro,
  Clock3,
  History,
  Plus,
  Search,
  Star,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";
import { entetesAuthentifiees } from "@/lib/auth";
import styles from "./page.module.css";

const API =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Article = {
  id: number;
  reference: string;
  designation: string;
  unite: string;
};

type Fournisseur = {
  id: number;
  code: string;
  raison_sociale: string;
  actif: boolean;
};

type Lien = {
  id: number;
  article_id: number;
  fournisseur_id: number;
  reference_fournisseur: string | null;
  prix_unitaire_ht: string | null;
  delai_jours: number | null;
  minimum_commande: string | null;
  fournisseur_prefere: boolean;
  date_maj_prix: string | null;
  article: Article;
  fournisseur: Fournisseur;
};

type PrixHistorique = {
  id: number;
  prix_unitaire_ht: string;
  date_effet: string;
  modifie_par: string | null;
  commentaire: string | null;
};

const euro = (value: string | number | null) =>
  value === null
    ? "—"
    : Number(value).toLocaleString("fr-FR", {
        style: "currency",
        currency: "EUR",
        maximumFractionDigits: 4,
      });

export default function TarifsFournisseursPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [liens, setLiens] = useState<Lien[]>([]);
  const [recherche, setRecherche] = useState("");
  const [edition, setEdition] = useState<Lien | null>(null);
  const [creation, setCreation] = useState(false);
  const [historique, setHistorique] = useState<{
    lien: Lien;
    lignes: PrixHistorique[];
  } | null>(null);
  const [form, setForm] = useState({
    article_id: "",
    fournisseur_id: "",
    reference_fournisseur: "",
    prix_unitaire_ht: "",
    delai_jours: "",
    minimum_commande: "",
    fournisseur_prefere: false,
    commentaire_prix: "",
  });
  const [toast, setToast] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  async function charger() {
    const headers = entetesAuthentifiees();
    try {
      const [a, f, l] = await Promise.all([
        fetch(`${API}/api/articles`, { headers }),
        fetch(`${API}/api/achats/fournisseurs`, { headers }),
        fetch(`${API}/api/achats/articles-fournisseurs`, { headers }),
      ]);
      if (!a.ok || !f.ok || !l.ok) throw new Error();
      setArticles(await a.json());
      setFournisseurs(await f.json());
      setLiens(await l.json());
    } catch {
      setToast({
        type: "error",
        message: "Impossible de charger les tarifs fournisseurs.",
      });
    }
  }

  useEffect(() => {
    charger();
  }, []);

  const visibles = useMemo(() => {
    const terme = recherche.trim().toLowerCase();
    if (!terme) return liens;
    return liens.filter(
      (lien) =>
        lien.article.reference.toLowerCase().includes(terme) ||
        lien.article.designation.toLowerCase().includes(terme) ||
        lien.fournisseur.code.toLowerCase().includes(terme) ||
        lien.fournisseur.raison_sociale.toLowerCase().includes(terme) ||
        (lien.reference_fournisseur ?? "")
          .toLowerCase()
          .includes(terme)
    );
  }, [liens, recherche]);

  function nouveau() {
    setForm({
      article_id: "",
      fournisseur_id: "",
      reference_fournisseur: "",
      prix_unitaire_ht: "",
      delai_jours: "",
      minimum_commande: "",
      fournisseur_prefere: false,
      commentaire_prix: "",
    });
    setCreation(true);
  }

  function modifier(lien: Lien) {
    setEdition(lien);
    setForm({
      article_id: String(lien.article_id),
      fournisseur_id: String(lien.fournisseur_id),
      reference_fournisseur: lien.reference_fournisseur ?? "",
      prix_unitaire_ht: lien.prix_unitaire_ht ?? "",
      delai_jours:
        lien.delai_jours === null ? "" : String(lien.delai_jours),
      minimum_commande: lien.minimum_commande ?? "",
      fournisseur_prefere: lien.fournisseur_prefere,
      commentaire_prix: "",
    });
  }

  async function enregistrer(event: FormEvent) {
    event.preventDefault();

    const payload = {
      article_id: Number(form.article_id),
      fournisseur_id: Number(form.fournisseur_id),
      reference_fournisseur:
        form.reference_fournisseur.trim() || null,
      prix_unitaire_ht:
        form.prix_unitaire_ht === ""
          ? null
          : Number(form.prix_unitaire_ht.replace(",", ".")),
      delai_jours:
        form.delai_jours === "" ? null : Number(form.delai_jours),
      minimum_commande:
        form.minimum_commande === ""
          ? null
          : Number(form.minimum_commande.replace(",", ".")),
      fournisseur_prefere: form.fournisseur_prefere,
      commentaire_prix:
        form.commentaire_prix.trim() || null,
    };

    const url = edition
      ? `${API}/api/achats/articles-fournisseurs/${edition.id}`
      : `${API}/api/achats/articles-fournisseurs`;

    const response = await fetch(url, {
      method: edition ? "PATCH" : "POST",
      headers: entetesAuthentifiees({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify(
        edition
          ? {
              reference_fournisseur: payload.reference_fournisseur,
              prix_unitaire_ht: payload.prix_unitaire_ht,
              delai_jours: payload.delai_jours,
              minimum_commande: payload.minimum_commande,
              fournisseur_prefere: payload.fournisseur_prefere,
              commentaire_prix: payload.commentaire_prix,
            }
          : payload
      ),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      setToast({
        type: "error",
        message: data?.detail ?? "Enregistrement impossible.",
      });
      return;
    }

    setCreation(false);
    setEdition(null);
    setToast({
      type: "success",
      message: "Conditions fournisseur enregistrées.",
    });
    await charger();
  }

  async function supprimer(lien: Lien) {
    if (
      !window.confirm(
        `Supprimer l’association ${lien.article.reference} / ${lien.fournisseur.code} ?`
      )
    ) {
      return;
    }

    const response = await fetch(
      `${API}/api/achats/articles-fournisseurs/${lien.id}`,
      {
        method: "DELETE",
        headers: entetesAuthentifiees(),
      }
    );
    if (!response.ok) {
      setToast({
        type: "error",
        message: "Suppression impossible.",
      });
      return;
    }
    await charger();
  }

  async function voirHistorique(lien: Lien) {
    const response = await fetch(
      `${API}/api/achats/articles-fournisseurs/${lien.id}/historique`,
      { headers: entetesAuthentifiees() }
    );
    if (!response.ok) {
      setToast({
        type: "error",
        message: "Historique indisponible.",
      });
      return;
    }
    setHistorique({
      lien,
      lignes: await response.json(),
    });
  }

  const modalOuverte = creation || edition !== null;

  return (
    <div>
      <div className="breadcrumb">
        Fournisseurs / Achats / Tarifs articles
      </div>

      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Référentiel achat</span>
          <h1>Tarifs fournisseurs par article</h1>
          <p>
            Références, prix, délais, minimums de commande et fournisseur
            préféré.
          </p>
        </div>
        <Button onClick={nouveau}>
          <Plus size={17} />
          Associer un fournisseur
        </Button>
      </div>

      <section className={styles.toolbar}>
        <label className="search-field">
          <Search size={17} />
          <input
            value={recherche}
            onChange={(event) => setRecherche(event.target.value)}
            placeholder="Article, fournisseur, référence fournisseur…"
          />
        </label>
      </section>

      <section className={styles.panel}>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Article</th>
                <th>Fournisseur</th>
                <th>Réf. fournisseur</th>
                <th>Prix HT</th>
                <th>Délai</th>
                <th>Minimum</th>
                <th>Préféré</th>
                <th>Maj prix</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {visibles.map((lien) => (
                <tr key={lien.id}>
                  <td>
                    <strong>{lien.article.reference}</strong>
                    <br />
                    <span>{lien.article.designation}</span>
                  </td>
                  <td>
                    <strong>{lien.fournisseur.code}</strong>
                    <br />
                    <span>{lien.fournisseur.raison_sociale}</span>
                  </td>
                  <td>{lien.reference_fournisseur ?? "—"}</td>
                  <td>
                    <strong>{euro(lien.prix_unitaire_ht)}</strong>
                  </td>
                  <td>
                    {lien.delai_jours === null
                      ? "—"
                      : `${lien.delai_jours} j`}
                  </td>
                  <td>
                    {lien.minimum_commande === null
                      ? "—"
                      : `${Number(
                          lien.minimum_commande
                        ).toLocaleString("fr-FR")} ${
                          lien.article.unite
                        }`}
                  </td>
                  <td>
                    {lien.fournisseur_prefere ? (
                      <span className={styles.preferred}>
                        <Star size={14} />
                        Préféré
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    {lien.date_maj_prix
                      ? new Intl.DateTimeFormat("fr-FR").format(
                          new Date(lien.date_maj_prix)
                        )
                      : "—"}
                  </td>
                  <td>
                    <div className={styles.actions}>
                      <button onClick={() => modifier(lien)}>
                        Modifier
                      </button>
                      <button onClick={() => voirHistorique(lien)}>
                        <History size={14} />
                      </button>
                      <button
                        className={styles.danger}
                        onClick={() => supprimer(lien)}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {visibles.length === 0 && (
                <tr>
                  <td colSpan={9} className={styles.empty}>
                    Aucune condition fournisseur enregistrée.
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
          style={{ zIndex: 10000 }}
          onMouseDown={() => {
            setCreation(false);
            setEdition(null);
          }}
        >
          <section
            className="modal-card modal-card-wide"
            style={{ position: "relative", zIndex: 10001 }}
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">Conditions d’achat</span>
                <h2>
                  {edition
                    ? `${edition.article.reference} / ${edition.fournisseur.code}`
                    : "Associer un fournisseur"}
                </h2>
              </div>
            </div>

            <form className={styles.form} onSubmit={enregistrer}>
              {!edition && (
                <>
                  <label>
                    Article *
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
                      <option value="">Sélectionner…</option>
                      {articles.map((article) => (
                        <option key={article.id} value={article.id}>
                          {article.reference} — {article.designation}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Fournisseur *
                    <select
                      required
                      value={form.fournisseur_id}
                      onChange={(event) =>
                        setForm({
                          ...form,
                          fournisseur_id: event.target.value,
                        })
                      }
                    >
                      <option value="">Sélectionner…</option>
                      {fournisseurs
                        .filter((fournisseur) => fournisseur.actif)
                        .map((fournisseur) => (
                          <option
                            key={fournisseur.id}
                            value={fournisseur.id}
                          >
                            {fournisseur.code} —{" "}
                            {fournisseur.raison_sociale}
                          </option>
                        ))}
                    </select>
                  </label>
                </>
              )}

              <label>
                Référence fournisseur
                <input
                  value={form.reference_fournisseur}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      reference_fournisseur: event.target.value,
                    })
                  }
                />
              </label>

              <label>
                <span>
                  <BadgeEuro size={15} /> Prix unitaire HT
                </span>
                <input
                  inputMode="decimal"
                  value={form.prix_unitaire_ht}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      prix_unitaire_ht: event.target.value,
                    })
                  }
                />
              </label>

              <label>
                <span>
                  <Clock3 size={15} /> Délai d’approvisionnement
                </span>
                <input
                  type="number"
                  min="0"
                  value={form.delai_jours}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      delai_jours: event.target.value,
                    })
                  }
                />
              </label>

              <label>
                Minimum de commande
                <input
                  inputMode="decimal"
                  value={form.minimum_commande}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      minimum_commande: event.target.value,
                    })
                  }
                />
              </label>

              <label className={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={form.fournisseur_prefere}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      fournisseur_prefere: event.target.checked,
                    })
                  }
                />
                <span>
                  <Star size={16} />
                  Fournisseur préféré pour cet article
                </span>
              </label>

              <label className={styles.wide}>
                Commentaire sur la modification de prix
                <textarea
                  value={form.commentaire_prix}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      commentaire_prix: event.target.value,
                    })
                  }
                  placeholder="Ex. nouveau tarif 2027, remise négociée…"
                />
              </label>

              <div className={styles.modalActions}>
                <Button type="submit">
                  Enregistrer
                </Button>
              </div>
            </form>
          </section>
        </div>
      )}

      {historique && (
        <div
          className="modal-backdrop"
          style={{ zIndex: 10000 }}
          onMouseDown={() => setHistorique(null)}
        >
          <section
            className="modal-card modal-card-wide"
            style={{ position: "relative", zIndex: 10001 }}
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">Historique tarifaire</span>
                <h2>
                  {historique.lien.article.reference} /{" "}
                  {historique.lien.fournisseur.code}
                </h2>
              </div>
            </div>

            <div className={styles.history}>
              {historique.lignes.map((ligne) => (
                <article key={ligne.id}>
                  <strong>{euro(ligne.prix_unitaire_ht)}</strong>
                  <span>
                    {new Intl.DateTimeFormat("fr-FR", {
                      dateStyle: "medium",
                      timeStyle: "short",
                    }).format(new Date(ligne.date_effet))}
                  </span>
                  <span>{ligne.modifie_par ?? "—"}</span>
                  <p>{ligne.commentaire ?? "—"}</p>
                </article>
              ))}
              {historique.lignes.length === 0 && (
                <p>Aucun historique tarifaire.</p>
              )}
            </div>
          </section>
        </div>
      )}

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
