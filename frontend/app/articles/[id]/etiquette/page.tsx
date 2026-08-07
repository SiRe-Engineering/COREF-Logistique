"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Printer } from "lucide-react";
import { Button } from "@/components/ui/Button";
import styles from "./page.module.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Article = {
  id: number;
  reference: string;
  designation: string;
  unite: string;
  famille_relation: { nom: string } | null;
  sous_famille_relation: { nom: string } | null;
};

export default function EtiquetteArticlePage() {
  const params = useParams<{ id: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [erreur, setErreur] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/api/articles/${params.id}`)
      .then(async (response) => {
        const data = await response.json().catch(() => null);
        if (!response.ok) throw new Error(data?.detail ?? "Chargement impossible.");
        setArticle(data);
      })
      .catch((cause) => setErreur(cause instanceof Error ? cause.message : "Chargement impossible."));
  }, [params.id]);

  if (erreur) return <main className={styles.message}>{erreur}</main>;
  if (!article) return <main className={styles.message}>Chargement…</main>;

  return (
    <main className={styles.page}>
      <div className={styles.actions}>
        <Button onClick={() => window.print()}><Printer size={16} />Imprimer</Button>
      </div>
      <section className={styles.label}>
        <div>
          <div className={styles.brand}>COREF LOGISTIQUE</div>
          <div className={styles.kind}>Étiquette article</div>
          <h1 className={styles.reference}>{article.reference}</h1>
          <p className={styles.designation}>{article.designation}</p>
          <div className={styles.meta}>
            <div><span>Famille :</span> {article.famille_relation?.nom ?? "—"}</div>
            <div><span>Sous-famille :</span> {article.sous_famille_relation?.nom ?? "—"}</div>
            <div><span>Unité :</span> {article.unite}</div>
          </div>
        </div>
        <div>
          <img
            className={styles.qr}
            src={`${API_URL}/api/documents/qrcode.svg?value=${encodeURIComponent(article.reference)}`}
            alt={`QR ${article.reference}`}
          />
          <div className={styles.scan}>Scanner en mode magasin</div>
        </div>
      </section>
    </main>
  );
}
