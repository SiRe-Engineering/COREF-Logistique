"use client";

import { entetesAuthentifiees } from "@/lib/auth";
import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  Pencil,
  Play,
  Plus,
  Printer,
  Search,
  Send,
  Trash2,
  XCircle,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { useAuth } from "@/components/auth/AuthProvider";
import {
  ActionBar,
  Button,
  Drawer,
  KpiCard,
  KpiGrid,
  SectionCard,
  StatusBadge,
} from "@/components/ui";
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
  quantite_manquante: string;
  statut: string;
  commentaire: string | null;
  motif_ecart: string | null;
  commentaire_preparateur: string | null;
  preparateur_effectif: string | null;
  date_debut_preparation: string | null;
  date_fin_preparation: string | null;
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


function tonStatutLigne(statut: string) {
  if (["PREPAREE", "EXPEDIEE"].includes(statut)) {
    return "success" as const;
  }
  if (statut === "PARTIELLE") {
    return "warning" as const;
  }
  if (statut === "INDISPONIBLE") {
    return "danger" as const;
  }
  if (statut === "EN_PREPARATION") return "information" as const;
  return "pending" as const;
}

function tonStatutPreparation(statut: string) {
  if (["PRETE", "EXPEDIEE"].includes(statut)) return "success" as const;
  if (statut === "EN_PREPARATION") return "information" as const;
  if (statut === "VALIDEE") return "validation" as const;
  return "pending" as const;
}

function libelleStatutLigne(statut: string) {
  const libelles: Record<string, string> = {
    A_PREPARER: "À préparer",
    PREPAREE: "Préparée",
    PARTIELLE: "Partielle",
    INDISPONIBLE: "Indisponible",
    EXPEDIEE: "Expédiée",
  };

  return libelles[statut] ?? statut;
}

export default function PreparationsPage() {
  const { utilisateur } = useAuth();
  const adminTechnique = utilisateur?.role === "ADMINISTRATEUR_TECHNIQUE";
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
    selection !== null && selection.statut === "BROUILLON";
  const executionActive =
    selection !== null && selection.statut === "EN_PREPARATION";


  const indicateurs = useMemo(() => {
    if (!selection) {
      return {
        progression: 0,
        lignesPreparees: 0,
        lignesTotales: 0,
        quantiteDemandee: 0,
        quantitePreparee: 0,
        quantiteManquante: 0,
        anomalies: 0,
      };
    }

    const quantiteDemandee = selection.lignes.reduce(
      (total, ligne) => total + Number(ligne.quantite_demandee),
      0
    );
    const quantitePreparee = selection.lignes.reduce(
      (total, ligne) => total + Number(ligne.quantite_preparee),
      0
    );
    const quantiteManquante = selection.lignes.reduce(
      (total, ligne) => total + Number(ligne.quantite_manquante),
      0
    );
    const lignesPreparees = selection.lignes.filter((ligne) =>
      ["PREPAREE", "REMPLACEMENT_ACCEPTE", "EXPEDIEE"].includes(
        ligne.statut
      )
    ).length;
    const anomalies = selection.lignes.filter((ligne) =>
      [
        "PARTIELLE",
        "INDISPONIBLE",
        "REMPLACEMENT_PROPOSE",
        "REMPLACEMENT_REFUSE",
      ].includes(ligne.statut)
    ).length;

    return {
      progression:
        quantiteDemandee > 0
          ? Math.min(
              100,
              Math.round((quantitePreparee / quantiteDemandee) * 100)
            )
          : 0,
      lignesPreparees,
      lignesTotales: selection.lignes.length,
      quantiteDemandee,
      quantitePreparee,
      quantiteManquante,
      anomalies,
    };
  }, [selection]);

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

  async function mettreAJourStatutLigne(
    ligne: Ligne,
    action: "COMPLETE" | "PARTIELLE" | "INDISPONIBLE" | "RESET"
  ) {
    if (!selection) return;

    let quantitePreparee = 0;
    let statut = "A_PREPARER";
    let motifEcart: string | null = null;

    if (action === "COMPLETE") {
      quantitePreparee = Number(ligne.quantite_demandee);
      statut = "PREPAREE";
    }

    if (action === "PARTIELLE") {
      const saisie = window.prompt(
        `Quantité réellement préparée pour ${ligne.article.designation} :`,
        ligne.quantite_preparee
      );
      if (saisie === null) return;

      quantitePreparee = Number(saisie);
      if (
        !Number.isFinite(quantitePreparee) ||
        quantitePreparee <= 0 ||
        quantitePreparee >= Number(ligne.quantite_demandee)
      ) {
        setToast({
          type: "error",
          message:
            "La quantité partielle doit être supérieure à zéro et inférieure à la quantité demandée.",
        });
        return;
      }

      const motif = window.prompt(
        "Motif de l’écart (obligatoire) :",
        ligne.motif_ecart ?? ""
      );
      if (!motif?.trim()) return;

      statut = "PARTIELLE";
      motifEcart = motif.trim();
    }

    if (action === "INDISPONIBLE") {
      const motif = window.prompt(
        "Pourquoi l’article est-il indisponible ?",
        ligne.motif_ecart ?? ""
      );
      if (!motif?.trim()) return;

      statut = "INDISPONIBLE";
      motifEcart = motif.trim();
    }

    const response = await fetch(
      `${API_URL}/api/preparations/${selection.id}/lignes/${ligne.id}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quantite_preparee: quantitePreparee,
          statut,
          motif_ecart: motifEcart,
        }),
      }
    );

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      setToast({
        type: "error",
        message:
          typeof data?.detail === "string"
            ? data.detail
            : "Mise à jour impossible.",
      });
      return;
    }

    await actualiserSelection(data);
    setToast({
      type: "success",
      message:
        action === "COMPLETE"
          ? "Ligne marquée comme complète."
          : action === "PARTIELLE"
            ? "Préparation partielle enregistrée."
            : action === "INDISPONIBLE"
              ? "Article déclaré indisponible."
              : "Ligne remise à préparer.",
    });
  }



  async function validerEtReserver() {
    if (!selection || selection.statut !== "BROUILLON") return;

    if (selection.lignes.length === 0) {
      setToast({
        type: "error",
        message: "Ajoute au moins une ligne avant de valider.",
      });
      return;
    }

    if (
      !window.confirm(
        `Valider ${selection.reference} et réserver toutes les quantités ?`
      )
    ) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/preparations/${selection.id}/valider`,
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
            : "Validation et réservation impossibles."
        );
      }

      await actualiserSelection(data);
      setToast({
        type: "success",
        message: "Préparation validée et stock réservé.",
      });
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Validation et réservation impossibles.",
      });
    }
  }


  async function demarrerPreparation() {
    if (!selection || selection.statut !== "VALIDEE") return;

    const response = await fetch(
      `${API_URL}/api/preparations/${selection.id}/demarrer`,
      {
        method: "POST",
        headers: entetesAuthentifiees(),
      }
    );

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      setToast({
        type: "error",
        message:
          typeof data?.detail === "string"
            ? data.detail
            : "Démarrage impossible.",
      });
      return;
    }

    await actualiserSelection(data);
    setToast({
      type: "success",
      message: "Préparation démarrée.",
    });
  }


  async function expedierPreparation() {
    if (!selection || selection.statut !== "PRETE") return;

    if (
      !window.confirm(
        `Expédier ${selection.reference} ?\n\n` +
          "Cette action va :\n" +
          "• décrémenter les stocks physiques ;\n" +
          "• libérer les réservations ;\n" +
          "• créer les mouvements de sortie.\n\n" +
          "Elle ne pourra pas être exécutée une seconde fois."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/preparations/${selection.id}/expedier`,
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
            : "Expédition impossible."
        );
      }

      await actualiserSelection(data);
      setToast({
        type: "success",
        message:
          "Préparation expédiée et mouvements de sortie créés.",
      });
    } catch (cause) {
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Expédition impossible.",
      });
    }
  }

  async function supprimerPreparation() {
    if (!selection || !adminTechnique) return;
    if (!window.confirm(`Supprimer définitivement ${selection.reference} ?`)) return;

    try {
      const response = await fetch(
        `${API_URL}/api/preparations/${selection.id}`,
        { method: "DELETE", headers: entetesAuthentifiees() }
      );
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string" ? data.detail : "Suppression impossible."
        );
      }
      setSelection(null);
      setToast({ type: "success", message: "Préparation supprimée." });
      await charger();
    } catch (cause) {
      setToast({
        type: "error",
        message: cause instanceof Error ? cause.message : "Suppression impossible.",
      });
    }
  }

  async function proposerRemplacement(ligne: Ligne) {
    if (!selection) return;

    const candidats = articles.filter(
      (article) => article.id !== ligne.article_id
    );
    const listeArticles = candidats
      .slice(0, 40)
      .map(
        (article) =>
          `${article.id} — ${article.reference} — ${article.designation}`
      )
      .join("\n");

    const saisieArticle = window.prompt(
      `ID de l’article de remplacement :\n\n${listeArticles}`
    );
    if (!saisieArticle) return;

    const articleId = Number(saisieArticle.split("—")[0].trim());
    const article = articles.find((element) => element.id === articleId);

    if (!article) {
      setToast({
        type: "error",
        message: "Article de remplacement invalide.",
      });
      return;
    }

    const listeEmplacements = emplacements
      .map(
        (emplacement) =>
          `${emplacement.id} — ${emplacement.code} — ${emplacement.nom}`
      )
      .join("\n");

    const saisieEmplacement = window.prompt(
      `ID de l’emplacement :\n\n${listeEmplacements}`,
      ligne.emplacement_source_id
        ? String(ligne.emplacement_source_id)
        : ""
    );
    if (!saisieEmplacement) return;

    const emplacementId = Number(
      saisieEmplacement.split("—")[0].trim()
    );
    const emplacementValide = emplacements.some(
      (emplacement) => emplacement.id === emplacementId
    );

    if (!emplacementValide) {
      setToast({
        type: "error",
        message: "Emplacement de remplacement invalide.",
      });
      return;
    }

    let lotId: number | null = null;

    if (article.famille_relation?.code === "BET") {
      const lotsCompatibles = lots.filter(
        (lot) => lot.article_id === articleId
      );
      const listeLots = lotsCompatibles
        .map(
          (lot) =>
            `${lot.id} — ${lot.numero_lot_fournisseur} — ${lot.date_peremption}`
        )
        .join("\n");

      const saisieLot = window.prompt(
        `ID du lot :\n\n${listeLots}`
      );
      if (!saisieLot) return;

      lotId = Number(saisieLot.split("—")[0].trim());

      if (!lotsCompatibles.some((lot) => lot.id === lotId)) {
        setToast({
          type: "error",
          message: "Lot de remplacement invalide.",
        });
        return;
      }
    }

    const quantite = window.prompt(
      "Quantité de remplacement :",
      ligne.quantite_demandee
    );
    if (!quantite) return;

    const quantiteRemplacement = Number(
      quantite.replace(",", ".")
    );

    if (
      !Number.isFinite(quantiteRemplacement) ||
      quantiteRemplacement <= 0
    ) {
      setToast({
        type: "error",
        message: "La quantité de remplacement doit être positive.",
      });
      return;
    }

    const commentaire = window.prompt(
      "Commentaire justifiant le remplacement (obligatoire) :"
    );
    if (!commentaire?.trim()) return;

    try {
      const response = await fetch(
        `${API_URL}/api/preparations/${selection.id}/lignes/${ligne.id}/remplacement`,
        {
          method: "POST",
          headers: entetesAuthentifiees({
            "Content-Type": "application/json",
          }),
          body: JSON.stringify({
            article_remplacement_id: articleId,
            lot_remplacement_id: lotId,
            emplacement_remplacement_id: emplacementId,
            quantite_remplacement: quantiteRemplacement,
            commentaire_remplacement: commentaire.trim(),
          }),
        }
      );

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        setToast({
          type: "error",
          message:
            typeof data?.detail === "string"
              ? data.detail
              : "Proposition impossible.",
        });
        return;
      }

      await actualiserSelection(data);
      setToast({
        type: "success",
        message: "Proposition de remplacement enregistrée.",
      });
    } catch {
      setToast({
        type: "error",
        message: "Impossible de joindre le serveur.",
      });
    }
  }

  async function deciderRemplacement(
    ligne: Ligne,
    decision: "accepter" | "refuser"
  ) {
    if (!selection) return;

    const commentaire = window.prompt(
      decision === "accepter"
        ? "Commentaire de validation (facultatif) :"
        : "Motif du refus (obligatoire) :"
    );

    if (decision === "refuser" && !commentaire?.trim()) return;

    try {
      const response = await fetch(
        `${API_URL}/api/preparations/${selection.id}/lignes/${ligne.id}/remplacement/${decision}`,
        {
          method: "POST",
          headers: entetesAuthentifiees({
            "Content-Type": "application/json",
          }),
          body: JSON.stringify({
            commentaire_decision: commentaire?.trim() || null,
          }),
        }
      );

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        setToast({
          type: "error",
          message:
            typeof data?.detail === "string"
              ? data.detail
              : "Décision impossible.",
        });
        return;
      }

      await actualiserSelection(data);
      setToast({
        type: "success",
        message:
          decision === "accepter"
            ? "Remplacement accepté."
            : "Remplacement refusé.",
      });
    } catch {
      setToast({
        type: "error",
        message: "Impossible de joindre le serveur.",
      });
    }
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
        eyebrow="Ordre de préparation"
        size="workspace"
        onClose={() => setSelection(null)}
      >
        {selection && (
          <div className={styles.workspace}>
            <section className={styles.identity}>
              <div>
                <div className={styles.identityTop}>
                  <h3>{selection.nom}</h3>
                  <StatusBadge
                    label={selection.statut.replaceAll("_", " ")}
                    tone={tonStatutPreparation(selection.statut)}
                  />
                </div>
                <p>
                  {selection.affaire.code_externe ||
                    selection.affaire.reference}{" "}
                  — {selection.affaire.nom}
                </p>
              </div>

              <div className={styles.identityActions}>
                <Button
                  variant="secondary"
                  onClick={() =>
                    window.open(
                      `/preparations/${selection.id}/impression`,
                      "_blank",
                      "noopener,noreferrer"
                    )
                  }
                >
                  <Printer size={16} />
                  Imprimer
                </Button>

                {editable && (
                  <Button
                    variant="secondary"
                    onClick={() => setEditionEntete(!editionEntete)}
                  >
                    <Pencil size={16} />
                    Modifier la préparation
                  </Button>
                )}
              </div>
            </section>

            <section className={styles.metaGrid}>
              <div>
                <span>Client</span>
                <strong>{selection.affaire.client ?? "—"}</strong>
              </div>
              <div>
                <span>Site / Zone</span>
                <strong>
                  {selection.affaire.site ?? "—"}
                  {selection.affaire.zone_intervention
                    ? ` / ${selection.affaire.zone_intervention}`
                    : ""}
                </strong>
              </div>
              <div>
                <span>Demandeur</span>
                <strong>{selection.demandeur ?? "—"}</strong>
              </div>
              <div>
                <span>Préparateur</span>
                <strong>{selection.preparateur ?? "—"}</strong>
              </div>
              <div>
                <span>Début</span>
                <strong>
                  {selection.date_besoin
                    ? new Intl.DateTimeFormat("fr-FR").format(
                        new Date(`${selection.date_besoin}T00:00:00`)
                      )
                    : "—"}
                </strong>
              </div>
              <div>
                <span>Véhicule</span>
                <strong>{selection.vehicule ?? "—"}</strong>
              </div>
            </section>

            <KpiGrid>
              <KpiCard
                label="Progression"
                value={`${indicateurs.progression} %`}
                description={`${indicateurs.lignesPreparees} / ${indicateurs.lignesTotales} lignes`}
              />
              <KpiCard
                label="Demandé"
                value={indicateurs.quantiteDemandee.toLocaleString("fr-FR")}
                description="Toutes unités confondues"
              />
              <KpiCard
                label="Préparé"
                value={indicateurs.quantitePreparee.toLocaleString("fr-FR")}
                description="Quantité enregistrée"
              />
              <KpiCard
                label="Manquant"
                value={indicateurs.quantiteManquante.toLocaleString("fr-FR")}
                description="Reste à traiter"
              />
              <KpiCard
                label="Anomalies"
                value={indicateurs.anomalies}
                description="Partiels ou indisponibles"
              />
            </KpiGrid>

            <div className={styles.progressBlock}>
              <div className={styles.progressTrack}>
                <span style={{ width: `${indicateurs.progression}%` }} />
              </div>
              <small>{indicateurs.progression}% de la préparation réalisée</small>
            </div>

            {editionEntete && (
              <SectionCard
                title="Informations de préparation"
                description="Demandeur, préparateur, véhicule et date de besoin."
              >
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
                  <div className={styles.inlineActions}>
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => setEditionEntete(false)}
                    >
                      Annuler
                    </Button>
                    <Button type="submit">Enregistrer</Button>
                  </div>
                </form>
              </SectionCard>
            )}

            {editable && (
              <SectionCard
                title={
                  ligneEditee
                    ? "Modifier le besoin"
                    : "Ajouter un article"
                }
                description="Les besoins validés alimentent les réservations."
              >
                <form className={styles.addLine} onSubmit={enregistrerLigne}>
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
              </SectionCard>
            )}

            {(selection.statut === "EN_PREPARATION" ||
              selection.statut === "PRETE") && (
              <section className={styles.executionProgress}>
                <div>
                  <span>Avancement</span>
                  <strong>{progression(selection)} %</strong>
                </div>
                <div className={styles.progressTrack}>
                  <div
                    className={styles.progressValue}
                    style={{ width: `${progression(selection)}%` }}
                  />
                </div>
                <small>
                  {
                    selection.lignes.filter(
                      (ligne) => ligne.statut === "PREPAREE"
                    ).length
                  }{" "}
                  / {selection.lignes.length} lignes complètes
                </small>
              </section>
            )}

            <SectionCard
              title="Ordre de préparation"
              description="Saisie directe des quantités et suivi des écarts."
              flush
            >
              <div className={styles.tableWrap}>
                <table className={styles.linesTable}>
                  <thead>
                    <tr>
                      <th>Statut</th>
                      <th>Article</th>
                      <th>Lot</th>
                      <th>Emplacement</th>
                      <th>Demandé</th>
                      <th>Manquant</th>
                      <th>Commentaire</th>
                      {(editable || executionActive) && <th aria-label="Actions" />}
                    </tr>
                  </thead>
                  <tbody>
                    {selection.lignes.map((ligne) => (
                      <tr key={ligne.id}>
                        <td>
                          <StatusBadge
                            label={libelleStatutLigne(ligne.statut)}
                            tone={tonStatutLigne(ligne.statut)}
                          />
                        </td>
                        <td>
                          <strong>{ligne.article.designation}</strong>
                          <small>{ligne.article.reference}</small>
                        </td>
                        <td>
                          {ligne.lot?.numero_lot_fournisseur ?? "—"}
                        </td>
                        <td>
                          {ligne.emplacement_source?.nom ?? "À définir"}
                        </td>
                        <td className={styles.numberCell}>
                          {Number(
                            ligne.quantite_demandee
                          ).toLocaleString("fr-FR")}{" "}
                          {ligne.article.unite}
                        </td>
                        <td className={styles.numberCell}>
                          {Number(
                            ligne.quantite_manquante
                          ).toLocaleString("fr-FR")}{" "}
                          {ligne.article.unite}
                        </td>
                        <td className={styles.commentCell}>
                          {ligne.article_remplacement ? (
                            <div className={styles.replacementSummary}>
                              <strong>
                                {ligne.article_remplacement.reference} —{" "}
                                {ligne.article_remplacement.designation}
                              </strong>
                              <span>
                                {ligne.quantite_remplacement}{" "}
                                {ligne.article_remplacement.unite}
                                {" — "}
                                {ligne.emplacement_remplacement?.nom ??
                                  "Emplacement non défini"}
                              </span>
                              {ligne.lot_remplacement && (
                                <small>
                                  Lot :{" "}
                                  {ligne.lot_remplacement.numero_lot_fournisseur}
                                </small>
                              )}
                              <small>
                                {ligne.commentaire_remplacement}
                              </small>
                              {ligne.decision_remplacement && (
                                <small>
                                  {ligne.decision_remplacement === "ACCEPTEE"
                                    ? "Remplacement accepté"
                                    : "Remplacement refusé"}
                                  {ligne.decision_par
                                    ? ` par ${ligne.decision_par}`
                                    : ""}
                                  {ligne.commentaire_decision
                                    ? ` — ${ligne.commentaire_decision}`
                                    : ""}
                                </small>
                              )}
                            </div>
                          ) : (
                            ligne.motif_ecart ||
                            ligne.commentaire_preparateur ||
                            ligne.commentaire ||
                            "—"
                          )}
                        </td>
                        {(editable || executionActive) && (
                          <td>
                            <div className={styles.rowActions}>
                              {selection.statut === "EN_PREPARATION" && (
                                <>
                                  <button
                                    type="button"
                                    className={styles.completeButton}
                                    onClick={() =>
                                      mettreAJourStatutLigne(
                                        ligne,
                                        "COMPLETE"
                                      )
                                    }
                                    title="Marquer complète"
                                    aria-label="Marquer la ligne complète"
                                  >
                                    ✓
                                  </button>
                                  <button
                                    type="button"
                                    className={styles.partialButton}
                                    onClick={() =>
                                      mettreAJourStatutLigne(
                                        ligne,
                                        "PARTIELLE"
                                      )
                                    }
                                    title="Marquer partielle"
                                    aria-label="Marquer la ligne partielle"
                                  >
                                    ½
                                  </button>
                                  <button
                                    type="button"
                                    className={styles.unavailableButton}
                                    onClick={() =>
                                      mettreAJourStatutLigne(
                                        ligne,
                                        "INDISPONIBLE"
                                      )
                                    }
                                    title="Marquer indisponible"
                                    aria-label="Marquer l’article indisponible"
                                  >
                                    !
                                  </button>
                                  <button
                                    type="button"
                                    className={styles.resetButton}
                                    onClick={() =>
                                      mettreAJourStatutLigne(ligne, "RESET")
                                    }
                                    title="Remettre à préparer"
                                    aria-label="Remettre la ligne à préparer"
                                  >
                                    ↺
                                  </button>
                                </>
                              )}
                              {["INDISPONIBLE", "REMPLACEMENT_REFUSE"].includes(
                                ligne.statut
                              ) && (
                                <button
                                  type="button"
                                  className={styles.replaceButton}
                                  onClick={() => proposerRemplacement(ligne)}
                                  title="Proposer un remplacement"
                                >
                                  ↻
                                </button>
                              )}

                              {ligne.statut === "REMPLACEMENT_PROPOSE" && (
                                <>
                                  <button
                                    type="button"
                                    className={styles.acceptButton}
                                    onClick={() =>
                                      deciderRemplacement(ligne, "accepter")
                                    }
                                    title="Accepter le remplacement"
                                  >
                                    ✓R
                                  </button>
                                  <button
                                    type="button"
                                    className={styles.rejectButton}
                                    onClick={() =>
                                      deciderRemplacement(ligne, "refuser")
                                    }
                                    title="Refuser le remplacement"
                                  >
                                    ✕R
                                  </button>
                                </>
                              )}

                              {editable && (
                                <>
                                  <button
                                    type="button"
                                    onClick={() => editerLigne(ligne)}
                                    title="Modifier le besoin"
                                  >
                                    <Pencil size={15} />
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => supprimerLigne(ligne)}
                                    title="Supprimer la ligne"
                                  >
                                    <Trash2 size={15} />
                                  </button>
                                </>
                              )}
                            </div>
                          </td>
                        )}
                      </tr>
                    ))}
                    {selection.lignes.length === 0 && (
                      <tr>
                        <td
                          colSpan={editable ? 8 : 7}
                          className={styles.emptyTable}
                        >
                          Aucun article ajouté.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </SectionCard>

            {selection.commentaire && (
              <SectionCard title="Remarques générales">
                <p className={styles.generalComment}>
                  {selection.commentaire}
                </p>
              </SectionCard>
            )}

            <ActionBar
              sticky
              secondary={
                adminTechnique ? (
                  <Button
                    variant="ghost"
                    onClick={supprimerPreparation}
                  >
                    <XCircle size={17} />
                    Supprimer
                  </Button>
                ) : null
              }
            >
              {selection.statut === "BROUILLON" && (
                <Button onClick={validerEtReserver}>
                  <CheckCircle2 size={17} />
                  Valider et réserver
                </Button>
              )}
              {selection.statut === "VALIDEE" && (
                <Button onClick={demarrerPreparation}>
                  <Play size={17} />
                  Démarrer la préparation
                </Button>
              )}
              {selection.statut === "EN_PREPARATION" && (
                <span className={styles.lockedMessage}>
                  Préparation en cours
                </span>
              )}
              {selection.statut === "PRETE" && (
                <Button onClick={expedierPreparation}>
                  <Send size={17} />
                  Expédier
                </Button>
              )}
              {selection.statut === "EXPEDIEE" && (
                <span className={styles.shippedMessage}>
                  Préparation expédiée
                </span>
              )}
            </ActionBar>
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
