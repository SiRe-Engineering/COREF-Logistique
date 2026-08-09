"use client";

import { apiFetch } from "@/lib/api";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { CheckCircle2, ClipboardList, Plus, Search, XCircle } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Toast } from "@/components/ui/Toast";
import { entetesAuthentifiees } from "@/lib/auth";
import styles from "./page.module.css";

type Article = {
  id: number;
  reference: string;
  designation: string;
  unite: string;
  famille_relation: { code: string } | null;
};
type Emplacement = { id: number; code: string; nom: string };
type Affaire = {
  id: number;
  reference: string;
  code_externe: string | null;
  nom: string;
  statut: string;
};
type Lot = { id: number; article_id: number; numero_lot_fournisseur: string };
type Demande = {
  id: number;
  reference: string;
  quantite: string;
  motif: string;
  commentaire: string | null;
  vehicule: string | null;
  statut: string;
  date_creation: string;
  motif_refus: string | null;
  demandeur: { nom_complet: string };
  validateur: { nom_complet: string } | null;
  article: Article;
  lot: Lot | null;
  emplacement_source: Emplacement;
  affaire: Affaire | null;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const VALIDATEURS = [
  "ADMINISTRATEUR_TECHNIQUE",
  "ADMINISTRATEUR_COREF",
  "RESPONSABLE_LOGISTIQUE",
  "RESPONSABLE_PRODUCTION",
  "CHARGE_AFFAIRES",
];

const formVide = {
  article_id: "",
  lot_id: "",
  emplacement_source_id: "",
  affaire_id: "",
  quantite: "",
  vehicule: "",
  motif: "",
  commentaire: "",
};

function badge(statut: string) {
  if (statut === "APPROUVEE") return { label: "Approuvée", tone: "success" as const };
  if (statut === "REFUSEE") return { label: "Refusée", tone: "beton" as const };
  return { label: "En attente", tone: "warning" as const };
}

export default function DemandesSortiePage() {
  const { utilisateur } = useAuth();
  const [demandes, setDemandes] = useState<Demande[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [emplacements, setEmplacements] = useState<Emplacement[]>([]);
  const [affaires, setAffaires] = useState<Affaire[]>([]);
  const [lots, setLots] = useState<Lot[]>([]);
  const [selection, setSelection] = useState<Demande | null>(null);
  const [modal, setModal] = useState(false);
  const [recherche, setRecherche] = useState("");
  const [filtre, setFiltre] = useState("");
  const [form, setForm] = useState(formVide);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const peutValider = VALIDATEURS.includes(utilisateur.role);

  async function charger() {
    const responses = await Promise.all([
      apiFetch(`${API_URL}/api/demandes-sortie`, { headers: entetesAuthentifiees() }),
      apiFetch(`${API_URL}/api/articles`),
      apiFetch(`${API_URL}/api/emplacements?racines_uniquement=false`),
      apiFetch(`${API_URL}/api/affaires`),
      apiFetch(`${API_URL}/api/lots-beton`),
    ]);
    if (responses.some((response) => !response.ok)) {
      setToast({ type: "error", message: "Impossible de charger les demandes." });
      return;
    }
    const data = await Promise.all(responses.map((response) => response.json()));
    setDemandes(data[0]);
    setArticles(data[1]);
    setEmplacements(data[2]);
    setAffaires(data[3]);
    setLots(data[4]);
  }

  useEffect(() => { charger(); }, []);

  const liste = useMemo(() => {
    const terme = recherche.toLowerCase().trim();
    return demandes.filter((demande) =>
      (!filtre || demande.statut === filtre) &&
      (!terme ||
        demande.reference.toLowerCase().includes(terme) ||
        demande.article.designation.toLowerCase().includes(terme) ||
        demande.demandeur.nom_complet.toLowerCase().includes(terme))
    );
  }, [demandes, recherche, filtre]);

  const article = articles.find((item) => item.id === Number(form.article_id));
  const lotObligatoire = article?.famille_relation?.code === "BET";
  const lotsArticle = lots.filter((lot) => lot.article_id === Number(form.article_id));

  async function creer(event: FormEvent) {
    event.preventDefault();
    const response = await apiFetch(`${API_URL}/api/demandes-sortie`, {
      method: "POST",
      headers: entetesAuthentifiees({ "Content-Type": "application/json" }),
      body: JSON.stringify({
        article_id: Number(form.article_id),
        lot_id: form.lot_id ? Number(form.lot_id) : null,
        emplacement_source_id: Number(form.emplacement_source_id),
        affaire_id: form.affaire_id ? Number(form.affaire_id) : null,
        quantite: Number(form.quantite),
        vehicule: form.vehicule || null,
        motif: form.motif,
        commentaire: form.commentaire || null,
      }),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      setToast({ type: "error", message: typeof data?.detail === "string" ? data.detail : "Création impossible." });
      return;
    }
    setModal(false);
    setForm(formVide);
    setSelection(data);
    await charger();
    setToast({
      type: "success",
      message: data.statut === "APPROUVEE"
        ? "La sortie a été exécutée directement."
        : "La demande a été transmise pour validation.",
    });
  }

  async function approuver() {
    if (!selection) return;
    const response = await apiFetch(`${API_URL}/api/demandes-sortie/${selection.id}/approuver`, {
      method: "POST",
      headers: entetesAuthentifiees(),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      setToast({ type: "error", message: data?.detail ?? "Approbation impossible." });
      return;
    }
    setSelection(data);
    await charger();
  }

  async function refuser() {
    if (!selection) return;
    const motif = window.prompt("Motif du refus :");
    if (!motif?.trim()) return;
    const response = await apiFetch(`${API_URL}/api/demandes-sortie/${selection.id}/refuser`, {
      method: "POST",
      headers: entetesAuthentifiees({ "Content-Type": "application/json" }),
      body: JSON.stringify({ motif_refus: motif.trim() }),
    });
    if (response.ok) {
      setSelection(await response.json());
      await charger();
    }
  }

  return (
    <div>
      <div className="breadcrumb">Exploitation / Demandes de sortie</div>
      <div className="page-heading page-heading-actions">
        <div>
          <span className="eyebrow">Workflow de validation</span>
          <h1>Demandes de sortie</h1>
          <p>Les utilisateurs standards soumettent une demande avant sortie.</p>
        </div>
        <Button variant="secondary" onClick={() => setModal(true)}>
          <Plus size={18} /> Nouvelle demande
        </Button>
      </div>

      <section className="content-card">
        <div className={styles.filters}>
          <label className="search-field">
            <Search size={17} />
            <input value={recherche} onChange={(e) => setRecherche(e.target.value)} placeholder="Référence, article ou demandeur" />
          </label>
          <select value={filtre} onChange={(e) => setFiltre(e.target.value)}>
            <option value="">Tous les statuts</option>
            <option value="EN_ATTENTE">En attente</option>
            <option value="APPROUVEE">Approuvée</option>
            <option value="REFUSEE">Refusée</option>
          </select>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Demande</th><th>Article</th><th>Quantité</th><th>Source</th>
                <th>Affaire</th><th>Demandeur</th><th>Date</th><th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {liste.map((demande) => {
                const statut = badge(demande.statut);
                return (
                  <tr key={demande.id} className="clickable-row" onClick={() => setSelection(demande)}>
                    <td><span className="reference-chip">{demande.reference}</span><strong className="table-title">{demande.motif}</strong></td>
                    <td><strong>{demande.article.designation}</strong><small className="table-subtext">{demande.article.reference}{demande.lot ? ` · lot ${demande.lot.numero_lot_fournisseur}` : ""}</small></td>
                    <td>{Number(demande.quantite).toLocaleString("fr-FR")} {demande.article.unite}</td>
                    <td>{demande.emplacement_source.nom}</td>
                    <td>{demande.affaire ? demande.affaire.code_externe || demande.affaire.reference : "Sortie libre"}</td>
                    <td>{demande.demandeur.nom_complet}</td>
                    <td>{new Intl.DateTimeFormat("fr-FR").format(new Date(demande.date_creation))}</td>
                    <td><Badge tone={statut.tone}>{statut.label}</Badge></td>
                  </tr>
                );
              })}
              {liste.length === 0 && (
                <tr><td colSpan={8} className="empty-state"><ClipboardList size={24} /><strong>Aucune demande</strong></td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <Drawer open={selection !== null} title={selection?.reference ?? ""} onClose={() => setSelection(null)}>
        {selection && (
          <div className={styles.detail}>
            <div className={styles.detailHeader}>
              <div><h3>{selection.article.designation}</h3><p>{selection.motif}</p></div>
              <Badge tone={badge(selection.statut).tone}>{badge(selection.statut).label}</Badge>
            </div>
            <dl className="detail-grid">
              <div><dt>Demandeur</dt><dd>{selection.demandeur.nom_complet}</dd></div>
              <div><dt>Quantité</dt><dd>{selection.quantite} {selection.article.unite}</dd></div>
              <div><dt>Emplacement</dt><dd>{selection.emplacement_source.nom}</dd></div>
              <div><dt>Affaire</dt><dd>{selection.affaire ? selection.affaire.code_externe || selection.affaire.reference : "Sortie libre"}</dd></div>
              <div><dt>Validateur</dt><dd>{selection.validateur?.nom_complet ?? "—"}</dd></div>
              <div><dt>Véhicule</dt><dd>{selection.vehicule ?? "—"}</dd></div>
            </dl>
            {selection.motif_refus && <div className={styles.refusal}><strong>Motif du refus</strong><p>{selection.motif_refus}</p></div>}
            {peutValider && selection.statut === "EN_ATTENTE" && (
              <div className="drawer-actions">
                <Button variant="ghost" onClick={refuser}><XCircle size={17} /> Refuser</Button>
                <Button onClick={approuver}><CheckCircle2 size={17} /> Approuver et sortir le stock</Button>
              </div>
            )}
          </div>
        )}
      </Drawer>

      {modal && (
        <div className="modal-backdrop" onMouseDown={() => setModal(false)}>
          <section className="modal-card" onMouseDown={(e) => e.stopPropagation()}>
            <div className="modal-header"><div><span className="eyebrow">Nouvelle sortie</span><h2>{peutValider ? "Enregistrer une sortie" : "Demander une sortie"}</h2></div></div>
            <form onSubmit={creer}>
              <div className="form-grid">
                <label className="field field-wide"><span>Article *</span>
                  <select required value={form.article_id} onChange={(e) => setForm({ ...form, article_id: e.target.value, lot_id: "" })}>
                    <option value="">Sélectionner</option>
                    {articles.map((item) => <option key={item.id} value={item.id}>{item.reference} — {item.designation}</option>)}
                  </select>
                </label>
                {lotObligatoire && (
                  <label className="field field-wide"><span>Lot béton *</span>
                    <select required value={form.lot_id} onChange={(e) => setForm({ ...form, lot_id: e.target.value })}>
                      <option value="">Sélectionner</option>
                      {lotsArticle.map((lot) => <option key={lot.id} value={lot.id}>{lot.numero_lot_fournisseur}</option>)}
                    </select>
                  </label>
                )}
                <label className="field"><span>Emplacement source *</span>
                  <select required value={form.emplacement_source_id} onChange={(e) => setForm({ ...form, emplacement_source_id: e.target.value })}>
                    <option value="">Sélectionner</option>
                    {emplacements.map((item) => <option key={item.id} value={item.id}>{item.nom}</option>)}
                  </select>
                </label>
                <label className="field"><span>Quantité *</span><input required type="number" min="0.001" step="0.001" value={form.quantite} onChange={(e) => setForm({ ...form, quantite: e.target.value })} /></label>
                <label className="field field-wide"><span>Affaire</span>
                  <select value={form.affaire_id} onChange={(e) => setForm({ ...form, affaire_id: e.target.value })}>
                    <option value="">Sortie libre</option>
                    {affaires.filter((a) => !["TERMINEE", "ANNULEE"].includes(a.statut)).map((a) => <option key={a.id} value={a.id}>{a.code_externe || a.reference} — {a.nom}</option>)}
                  </select>
                </label>
                <label className="field"><span>Véhicule</span><input value={form.vehicule} onChange={(e) => setForm({ ...form, vehicule: e.target.value })} /></label>
                <label className="field"><span>Motif *</span><input required value={form.motif} onChange={(e) => setForm({ ...form, motif: e.target.value })} /></label>
                <label className="field field-wide"><span>Commentaire</span><textarea rows={3} value={form.commentaire} onChange={(e) => setForm({ ...form, commentaire: e.target.value })} /></label>
              </div>
              <div className="modal-actions">
                <Button type="button" variant="ghost" onClick={() => setModal(false)}>Annuler</Button>
                <Button type="submit">{peutValider ? "Sortir le stock" : "Soumettre la demande"}</Button>
              </div>
            </form>
          </section>
        </div>
      )}
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
