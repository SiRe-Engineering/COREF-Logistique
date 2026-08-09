"use client";

import { apiFetch } from "@/lib/api";

import Link from "next/link";
import {
  Barcode,
  Boxes,
  ClipboardCheck,
  PackageCheck,
  RotateCcw,
  Search,
  Warehouse,
  X,
} from "lucide-react";
import {
  FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { entetesAuthentifiees } from "@/lib/auth";
import { Toast } from "@/components/ui/Toast";
import styles from "./page.module.css";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Emplacement = {
  id: number;
  code: string;
  nom: string;
  quantite_physique: string;
  quantite_reservee: string;
  quantite_disponible: string;
};

type Resultat = {
  type: "ARTICLE" | "LOT";
  valeur: string;
  article: null | {
    id: number;
    reference: string;
    designation: string;
    unite: string;
    famille: string | null;
    sous_famille: string | null;
    quantite_physique: string;
    quantite_reservee: string;
    quantite_disponible: string;
    emplacements: Emplacement[];
  };
  lot: null | {
    id: number;
    reference_interne: string;
    numero_lot_fournisseur: string;
    article_id: number;
    article_reference: string;
    article_designation: string;
    unite: string;
    date_peremption: string;
    emplacements: Emplacement[];
  };
};

function nombre(value: string) {
  return Number(value).toLocaleString("fr-FR", {
    maximumFractionDigits: 3,
  });
}

export default function MagasinPage() {
  const [scan, setScan] = useState("");
  const [resultat, setResultat] = useState<Resultat | null>(null);
  const [chargement, setChargement] = useState(false);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, [resultat]);

  async function rechercher(event?: FormEvent) {
    event?.preventDefault();
    const valeur = scan.trim();
    if (!valeur || chargement) return;

    setChargement(true);
    try {
      const response = await apiFetch(
        `${API_URL}/api/magasin/scan/${encodeURIComponent(valeur)}`,
        { headers: entetesAuthentifiees() }
      );
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : "Code introuvable."
        );
      }

      setResultat(data);
      setScan("");
    } catch (cause) {
      setResultat(null);
      setToast({
        type: "error",
        message:
          cause instanceof Error
            ? cause.message
            : "Code introuvable.",
      });
      setScan("");
    } finally {
      setChargement(false);
      window.setTimeout(() => inputRef.current?.focus(), 50);
    }
  }

  const article = resultat?.article;
  const lot = resultat?.lot;
  const emplacements = article?.emplacements ?? lot?.emplacements ?? [];
  const unite = article?.unite ?? lot?.unite ?? "";

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <span className="eyebrow">Interface opérateur</span>
          <h1>Mode magasin</h1>
          <p>
            Scannez une référence article, une référence de lot ou un
            numéro de lot fournisseur.
          </p>
        </div>
        <Barcode size={42} strokeWidth={1.5} />
      </div>

      <form className={styles.scanBox} onSubmit={rechercher}>
        <Barcode size={30} />
        <input
          ref={inputRef}
          autoFocus
          autoComplete="off"
          value={scan}
          onChange={(event) => setScan(event.target.value)}
          placeholder="Scanner ou saisir une référence…"
          aria-label="Code à scanner"
        />
        {scan && (
          <button
            type="button"
            className={styles.clear}
            onClick={() => {
              setScan("");
              inputRef.current?.focus();
            }}
          >
            <X size={22} />
          </button>
        )}
        <button
          type="submit"
          className={styles.scanButton}
          disabled={!scan.trim() || chargement}
        >
          <Search size={22} />
          {chargement ? "Recherche…" : "Rechercher"}
        </button>
      </form>

      <section className={styles.actions}>
        <Link href="/preparations">
          <PackageCheck size={30} />
          <strong>Préparations</strong>
          <span>Préparer et expédier</span>
        </Link>
        <Link href="/preparations">
          <RotateCcw size={30} />
          <strong>Retours</strong>
          <span>Réintégrer du chantier</span>
        </Link>
        <Link href="/inventaires">
          <ClipboardCheck size={30} />
          <strong>Inventaires</strong>
          <span>Compter le stock</span>
        </Link>
        <Link href="/stocks">
          <Warehouse size={30} />
          <strong>Stocks</strong>
          <span>Consulter les emplacements</span>
        </Link>
      </section>

      {!resultat && (
        <section className={styles.idle}>
          <Barcode size={58} strokeWidth={1.2} />
          <strong>Lecteur prêt</strong>
          <span>
            Un scanner USB ou Bluetooth configuré comme clavier peut
            écrire directement dans le champ ci-dessus puis envoyer Entrée.
          </span>
        </section>
      )}

      {article && (
        <section className={styles.result}>
          <div className={styles.resultTitle}>
            <div>
              <span>Article</span>
              <h2>{article.designation}</h2>
              <strong>{article.reference}</strong>
            </div>
            <Boxes size={34} />
          </div>

          <div className={styles.kpis}>
            <div>
              <span>Physique</span>
              <strong>{nombre(article.quantite_physique)} {article.unite}</strong>
            </div>
            <div>
              <span>Réservé</span>
              <strong>{nombre(article.quantite_reservee)} {article.unite}</strong>
            </div>
            <div>
              <span>Disponible</span>
              <strong>{nombre(article.quantite_disponible)} {article.unite}</strong>
            </div>
          </div>

          <Emplacements
            emplacements={emplacements}
            unite={article.unite}
          />
        </section>
      )}

      {lot && (
        <section className={styles.result}>
          <div className={styles.resultTitle}>
            <div>
              <span>Lot béton</span>
              <h2>{lot.article_designation}</h2>
              <strong>
                {lot.reference_interne} · {lot.numero_lot_fournisseur}
              </strong>
            </div>
            <Boxes size={34} />
          </div>

          <div className={styles.lotInfo}>
            <span>Article : {lot.article_reference}</span>
            <span>
              Péremption :{" "}
              {new Date(`${lot.date_peremption}T12:00:00`).toLocaleDateString(
                "fr-FR"
              )}
            </span>
          </div>

          <Emplacements
            emplacements={emplacements}
            unite={lot.unite}
          />
        </section>
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

function Emplacements({
  emplacements,
  unite,
}: {
  emplacements: Emplacement[];
  unite: string;
}) {
  return (
    <div className={styles.locations}>
      <h3>Emplacements</h3>
      {emplacements.length === 0 ? (
        <div className={styles.noStock}>Aucun stock enregistré.</div>
      ) : (
        emplacements.map((emplacement) => (
          <article key={emplacement.id}>
            <div>
              <Warehouse size={24} />
              <div>
                <strong>{emplacement.code}</strong>
                <span>{emplacement.nom}</span>
              </div>
            </div>
            <div className={styles.locationQty}>
              <span>
                Physique {nombre(emplacement.quantite_physique)} {unite}
              </span>
              <span>
                Réservé {nombre(emplacement.quantite_reservee)} {unite}
              </span>
              <strong>
                Disponible {nombre(emplacement.quantite_disponible)} {unite}
              </strong>
            </div>
          </article>
        ))
      )}
    </div>
  );
}
