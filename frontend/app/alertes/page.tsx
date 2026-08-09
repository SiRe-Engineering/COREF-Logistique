"use client";

import { apiFetch } from "@/lib/api";
import Link from "next/link";
import {useEffect,useMemo,useState} from "react";
import {AlertTriangle,Bell,ChevronRight,CircleAlert,Info,RefreshCcw,Search} from "lucide-react";
import {Button} from "@/components/ui/Button";
import {Toast} from "@/components/ui/Toast";
import {entetesAuthentifiees} from "@/lib/auth";
import styles from "./page.module.css";

const API=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8000";
const cats=["TOUTES","STOCK","APPRO","PREPARATION","MATERIEL","INVENTAIRE"];

export default function Page(){
 const[data,setData]=useState<any>(null),[cat,setCat]=useState("TOUTES"),[q,setQ]=useState(""),[toast,setToast]=useState<any>(null);
 async function load(){try{const r=await apiFetch(`${API}/api/alertes-logistiques`,{headers:entetesAuthentifiees()});const d=await r.json();if(!r.ok)throw new Error(d?.detail??"Chargement impossible");setData(d)}catch(e:any){setToast({type:"error",message:e.message})}}
 useEffect(()=>{load()},[]);
 const rows=useMemo(()=>{const s=q.toLowerCase();return (data?.alertes??[]).filter((x:any)=>(cat==="TOUTES"||x.categorie===cat)&&(!s||`${x.titre} ${x.detail}`.toLowerCase().includes(s)))},[data,cat,q]);
 return <div>
  <div className="breadcrumb">Pilotage / Centre d'alertes</div>
  <div className="page-heading page-heading-actions"><div><span className="eyebrow">Priorités opérationnelles</span><h1>Centre d'alertes</h1><p>Une vue unique des points nécessitant une action logistique.</p></div><Button variant="secondary" onClick={load}><RefreshCcw size={17}/>Actualiser</Button></div>
  <section className={styles.kpis}>
   <article><Bell/><span>Total</span><strong>{data?.total??0}</strong></article>
   <article className={styles.critical}><CircleAlert/><span>Critiques</span><strong>{data?.critiques??0}</strong></article>
   <article className={styles.warning}><AlertTriangle/><span>Attention</span><strong>{data?.attention??0}</strong></article>
   <article><Info/><span>Information</span><strong>{data?.info??0}</strong></article>
  </section>
  <section className={styles.panel}>
   <div className={styles.toolbar}><label className="search-field"><Search size={17}/><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Rechercher une alerte…"/></label><div className={styles.filters}>{cats.map(x=><button key={x} className={cat===x?styles.active:""} onClick={()=>setCat(x)}>{x}</button>)}</div></div>
   <div className={styles.list}>{rows.map((x:any)=><Link href={x.href} key={x.key} className={styles.row}><span className={`${styles.level} ${styles[x.niveau.toLowerCase()]}`}>{x.niveau}</span><div><strong>{x.titre}</strong><p>{x.detail}</p></div><span className={styles.category}>{x.categorie}</span><ChevronRight size={18}/></Link>)}{!rows.length&&<div className={styles.empty}>Aucune alerte pour ce filtre.</div>}</div>
  </section>
  {toast&&<Toast type={toast.type} message={toast.message} onClose={()=>setToast(null)}/>}
 </div>
}
