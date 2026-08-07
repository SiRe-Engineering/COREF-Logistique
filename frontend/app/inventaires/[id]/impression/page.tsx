"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Printer } from "lucide-react";
import { Button } from "@/components/ui/Button";
import styles from "./page.module.css";

const API_URL=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8000";
type Inventaire={reference:string;nom:string;statut:string;operateur:string|null;valide_par:string|null;lignes:Array<{
 id:number;quantite_theorique:string;quantite_comptee:string|null;ecart:string|null;commentaire:string|null;
 article:{reference:string;designation:string;unite:string};
 lot:{numero_lot_fournisseur:string}|null;
 emplacement:{code:string;nom:string};
}>};

export default function ImpressionInventaire(){
 const params=useParams<{id:string}>(); const [data,setData]=useState<Inventaire|null>(null); const [erreur,setErreur]=useState("");
 useEffect(()=>{fetch(`${API_URL}/api/inventaires/${params.id}`).then(async r=>{const d=await r.json().catch(()=>null);if(!r.ok)throw new Error(d?.detail??"Chargement impossible.");setData(d)}).catch(e=>setErreur(e instanceof Error?e.message:"Chargement impossible."));},[params.id]);
 if(erreur)return <main className={styles.message}>{erreur}</main>; if(!data)return <main className={styles.message}>Chargement…</main>;
 return <main className={styles.page}>
  <div className={styles.actions}><Button onClick={()=>window.print()}><Printer size={16}/>Imprimer / PDF</Button></div>
  <header className={styles.header}><div className={styles.brand}>COREF LOGISTIQUE</div><div className={styles.title}><span>FICHE D’INVENTAIRE</span><h1>{data.reference}</h1></div><div className={styles.meta}>{data.statut.replaceAll("_"," ")}</div></header>
  <section className={styles.identity}><div><span>Inventaire</span><strong>{data.nom}</strong></div><div><span>Opérateur</span><strong>{data.operateur??"—"}</strong></div><div><span>Validé par</span><strong>{data.valide_par??"—"}</strong></div><div><span>Date impression</span><strong>{new Intl.DateTimeFormat("fr-FR").format(new Date())}</strong></div></section>
  <table className={styles.table}><thead><tr><th>Article</th><th>Lot</th><th>Emplacement</th><th>Théorique</th><th>Compté</th><th>Écart</th><th>Observation</th></tr></thead>
  <tbody>{data.lignes.map(l=><tr key={l.id}><td><strong>{l.article.reference}</strong><br/>{l.article.designation}</td><td>{l.lot?.numero_lot_fournisseur??"—"}</td><td>{l.emplacement.code} — {l.emplacement.nom}</td><td className={styles.num}>{Number(l.quantite_theorique).toLocaleString("fr-FR")} {l.article.unite}</td><td className={styles.num}>{l.quantite_comptee===null?"":`${Number(l.quantite_comptee).toLocaleString("fr-FR")} ${l.article.unite}`}</td><td className={styles.num}>{l.ecart===null?"":Number(l.ecart).toLocaleString("fr-FR")}</td><td>{l.commentaire??""}</td></tr>)}</tbody></table>
  <section className={styles.signatures}><div><span>Comptage réalisé par</span></div><div><span>Date / heure</span></div><div><span>Signature / validation</span></div></section>
 </main>
}
