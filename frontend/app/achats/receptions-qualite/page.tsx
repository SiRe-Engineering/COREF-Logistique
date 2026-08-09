"use client";

import { apiFetch } from "@/lib/api";
import {useEffect,useState} from "react";
import Link from "next/link";
import {AlertTriangle,CheckCircle2,RefreshCcw,Search} from "lucide-react";
import {Button} from "@/components/ui/Button";
import {Toast} from "@/components/ui/Toast";
import {entetesAuthentifiees} from "@/lib/auth";
import styles from "./page.module.css";
const API=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8000";
export default function Page(){
 const[data,setData]=useState<any[]>([]),[search,setSearch]=useState(""),[toast,setToast]=useState<any>(null);
 async function load(){try{const r=await apiFetch(`${API}/api/receptions-qualite`,{headers:entetesAuthentifiees()});if(!r.ok)throw 0;setData(await r.json())}catch{setToast({type:"error",message:"Impossible de charger les contrôles réception."})}}
 useEffect(()=>{load()},[]);
 const t=search.toLowerCase().trim();const rows=data.filter(x=>!t||x.commande_reference.toLowerCase().includes(t)||x.article_reference.toLowerCase().includes(t)||x.article_designation.toLowerCase().includes(t)||x.fournisseur.toLowerCase().includes(t));
 return <div><div className="breadcrumb">Fournisseurs / Achats / Contrôle réception</div><div className="page-heading page-heading-actions"><div><span className="eyebrow">Qualité réception</span><h1>Contrôles réception fournisseur</h1><p>BL, conformité visuelle, réserves et présence FDS pour le béton.</p></div><Button variant="secondary" onClick={load}><RefreshCcw size={17}/>Actualiser</Button></div><section className={styles.kpis}><article><CheckCircle2/><span>Conformes</span><strong>{data.filter(x=>x.statut_qualite==="CONFORME").length}</strong></article><article><AlertTriangle/><span>À contrôler</span><strong>{data.filter(x=>x.statut_qualite==="A_CONTROLER").length}</strong></article><article><AlertTriangle/><span>Sous réserve</span><strong>{data.filter(x=>x.statut_qualite==="SOUS_RESERVE").length}</strong></article><article><AlertTriangle/><span>Non conformes</span><strong>{data.filter(x=>x.statut_qualite==="NON_CONFORME").length}</strong></article></section><section className={styles.panel}><div className={styles.toolbar}><label className="search-field"><Search size={17}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Commande, fournisseur ou article…"/></label></div><table className={styles.table}><thead><tr><th>Date</th><th>Commande</th><th>Fournisseur</th><th>Article</th><th>Lot</th><th>Qté</th><th>BL</th><th>FDS</th><th>Qualité</th><th>Réserve</th><th>NCF</th></tr></thead><tbody>{rows.map(x=><tr key={x.id}><td>{new Intl.DateTimeFormat("fr-FR",{dateStyle:"short",timeStyle:"short"}).format(new Date(x.date_reception))}</td><td><strong>{x.commande_reference}</strong></td><td>{x.fournisseur}</td><td><strong>{x.article_reference}</strong><br/><span>{x.article_designation}</span></td><td>{x.lot_reference??"—"}</td><td>{x.quantite} {x.unite}</td><td>{x.bon_livraison_reference??"—"}</td><td>{x.fds_presente==null?"N/A":x.fds_presente?"Présente":"Manquante"}</td><td><span className={styles.badge}>{x.statut_qualite.replaceAll("_"," ")}</span></td><td>{x.reserve_commentaire??"—"}</td><td>{x.ncf_reference?<Link href="/achats/non-conformites">{x.ncf_reference}</Link>:["SOUS_RESERVE","NON_CONFORME"].includes(x.statut_qualite)?<Link href="/achats/non-conformites">Créer</Link>:"—"}</td></tr>)}{!rows.length&&<tr><td colSpan={11} className={styles.empty}>Aucune réception contrôlée.</td></tr>}</tbody></table></section>{toast&&<Toast type={toast.type} message={toast.message} onClose={()=>setToast(null)}/>}</div>
}
