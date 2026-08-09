"use client";

import { apiFetch } from "@/lib/api";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Printer } from "lucide-react";
import { Button } from "@/components/ui/Button";
import styles from "./page.module.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Preparation = {
  id:number; reference:string; nom:string; statut:string; demandeur:string|null; preparateur:string|null;
  vehicule:string|null; date_expedition:string|null;
  affaire:{reference:string;code_externe:string|null;nom:string;client:string|null;site:string|null;zone_intervention:string|null};
  lignes:Array<{
    id:number; quantite_demandee:string; quantite_preparee:string; quantite_expediee:string; quantite_retournee:string;
    commentaire:string|null; motif_ecart:string|null;
    article:{reference:string;designation:string;unite:string};
    lot:{numero_lot_fournisseur:string}|null;
    emplacement_source:{code:string;nom:string}|null;
  }>;
};

export default function DocumentPreparation() {
  const params=useParams<{id:string}>();
  const [p,setP]=useState<Preparation|null>(null);
  const [erreur,setErreur]=useState("");
  useEffect(()=>{apiFetch(`${API_URL}/api/preparations/${params.id}`)
    .then(async r=>{const d=await r.json().catch(()=>null);if(!r.ok)throw new Error(d?.detail??"Chargement impossible.");setP(d)})
    .catch(e=>setErreur(e instanceof Error?e.message:"Chargement impossible."));},[params.id]);
  if(erreur)return <main className={styles.message}>{erreur}</main>;
  if(!p)return <main className={styles.message}>Chargement…</main>;
  const isRetour=false;
  const titre=isRetour?"FICHE DE RETOUR CHANTIER":"BON D’EXPÉDITION";
  return <main className={styles.page}>
    <div className={styles.actions}><Button onClick={()=>window.print()}><Printer size={16}/>Imprimer / PDF</Button></div>
    <header className={styles.header}>
      <div className={styles.brand}>COREF LOGISTIQUE</div>
      <div className={styles.title}><span>{titre}</span><h1>{p.reference}</h1></div>
      <div className={styles.meta}>Édité le {new Intl.DateTimeFormat("fr-FR",{dateStyle:"short",timeStyle:"short"}).format(new Date())}</div>
    </header>
    <section className={styles.identity}>
      <div><span>Affaire</span><strong>{p.affaire.code_externe||p.affaire.reference} — {p.affaire.nom}</strong></div>
      <div><span>Client</span><strong>{p.affaire.client??"—"}</strong></div>
      <div><span>Site / zone</span><strong>{p.affaire.site??"—"} / {p.affaire.zone_intervention??"—"}</strong></div>
      <div><span>Véhicule</span><strong>{p.vehicule??"—"}</strong></div>
    </section>
    <table className={styles.table}>
      <thead><tr><th>Article</th><th>Lot</th><th>Emplacement</th><th>{isRetour?"Expédié":"Préparé"}</th><th>{isRetour?"Déjà retourné":"Expédié"}</th>{isRetour&&<th>À retourner</th>}<th>Observations</th></tr></thead>
      <tbody>{p.lignes.map(l=>{
        const expedie=Number(l.quantite_expediee||0), retourne=Number(l.quantite_retournee||0);
        return <tr key={l.id}>
          <td><strong>{l.article.reference}</strong><br/>{l.article.designation}</td>
          <td>{l.lot?.numero_lot_fournisseur??"—"}</td>
          <td>{l.emplacement_source?.code??"—"}</td>
          <td className={styles.num}>{Number(isRetour?l.quantite_expediee:l.quantite_preparee).toLocaleString("fr-FR")} {l.article.unite}</td>
          <td className={styles.num}>{Number(isRetour?l.quantite_retournee:l.quantite_expediee).toLocaleString("fr-FR")} {l.article.unite}</td>
          {isRetour&&<td className={styles.num}>{Math.max(0,expedie-retourne).toLocaleString("fr-FR")} {l.article.unite}</td>}
          <td>{l.motif_ecart||l.commentaire||""}</td>
        </tr>})}</tbody>
    </table>
    <section className={styles.signatures}>
      <div><span>{isRetour?"Retour contrôlé par":"Préparé / chargé par"}</span></div>
      <div><span>Date / heure</span></div>
      <div><span>Signature</span></div>
    </section>
  </main>;
}
