"use client";

import { apiFetch } from "@/lib/api";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Printer } from "lucide-react";
import { Button } from "@/components/ui/Button";
import styles from "./page.module.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Lot = {
  id: number;
  reference_interne: string;
  numero_lot_fournisseur: string;
  date_fabrication: string;
  date_peremption: string;
  fournisseur: string | null;
  article: { reference: string; designation: string; unite: string };
};

function dateFr(value: string) {
  return new Intl.DateTimeFormat("fr-FR").format(new Date(`${value}T12:00:00`));
}

export default function EtiquetteLotPage() {
  const params = useParams<{ id: string }>();
  const [lot, setLot] = useState<Lot | null>(null);
  const [erreur, setErreur] = useState("");

  useEffect(() => {
    apiFetch(`${API_URL}/api/lots-beton/${params.id}`)
      .then(async (response) => {
        const data = await response.json().catch(() => null);
        if (!response.ok) throw new Error(data?.detail ?? "Chargement impossible.");
        setLot(data);
      })
      .catch((cause) => setErreur(cause instanceof Error ? cause.message : "Chargement impossible."));
  }, [params.id]);

  if (erreur) return <main className={styles.message}>{erreur}</main>;
  if (!lot) return <main className={styles.message}>Chargement…</main>;

  return (
    <main className={styles.page}>
      <div className={styles.actions}>
        <Button onClick={() => window.print()}><Printer size={16} />Imprimer</Button>
      </div>
      <section className={styles.label}>
        <div>
          <div className={styles.brand}>COREF LOGISTIQUE</div>
          <div className={styles.kind}>Lot béton</div>
          <h1 className={styles.reference}>{lot.reference_interne}</h1>
          <p className={styles.designation}>{lot.article.reference} — {lot.article.designation}</p>
          <div className={styles.meta}>
            <div><span>Lot fournisseur :</span> {lot.numero_lot_fournisseur}</div>
            <div><span>Fabrication :</span> {dateFr(lot.date_fabrication)}</div>
            <div><span>Péremption :</span> <strong>{dateFr(lot.date_peremption)}</strong></div>
            <div><span>Fournisseur :</span> {lot.fournisseur ?? "—"}</div>
          </div>
        </div>
        <div>
          <img
            className={styles.qr}
            src={`${API_URL}/api/documents/qrcode.svg?value=${encodeURIComponent(lot.reference_interne)}`}
            alt={`QR ${lot.reference_interne}`}
          />
          <div className={styles.scan}>Scanner en mode magasin</div>
        </div>
      </section>
    </main>
  );
}
