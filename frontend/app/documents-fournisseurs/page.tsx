"use client";

import { apiFetch } from "@/lib/api";

import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { FileCheck2, FileText, Plus, Search, ShieldAlert, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";
import { entetesAuthentifiees } from "@/lib/auth";
import styles from "./page.module.css";

const API=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8000";

type Lot={id:number;reference_interne:string;numero_lot_fournisseur:string;article:{reference:string;designation:string}};
type Doc={id:number;type_document:string;nom_fichier:string;type_mime:string;taille_octets:number;lot_beton_id:number|null;reference_document:string|null;date_document:string|null;date_expiration:string|null;date_depot:string;depose_par:string|null};
type Statut={lot_id:number;reference_interne:string;article_reference:string;article_designation:string;certificat_present:boolean;fds_presente:boolean;document_expire:boolean;statut:string;documents:Doc[]};

const labels:any={CERTIFICAT:"Certificat fournisseur",FDS:"FDS",FICHE_TECHNIQUE:"Fiche technique",BON_LIVRAISON:"Bon de livraison",AUTRE:"Autre"};

export default function DocumentsFournisseurs(){
 const [lots,setLots]=useState<Lot[]>([]),[docs,setDocs]=useState<Doc[]>([]),[statuts,setStatuts]=useState<Statut[]>([]);
 const [search,setSearch]=useState(""),[modal,setModal]=useState(false),[toast,setToast]=useState<any>(null);
 const [form,setForm]=useState({lot_beton_id:"",type_document:"CERTIFICAT",reference_document:"",date_document:"",date_expiration:"",commentaire:"",file:null as File|null});

 async function load(){
  try{
   const h=entetesAuthentifiees();
   const [l,d,s]=await Promise.all([
    apiFetch(`${API}/api/lots-beton`),
    apiFetch(`${API}/api/documents-fournisseurs`,{headers:h}),
    apiFetch(`${API}/api/documents-fournisseurs/lots/statuts`,{headers:h})
   ]);
   if(!l.ok||!d.ok||!s.ok)throw 0;
   setLots(await l.json());setDocs(await d.json());setStatuts(await s.json());
  }catch{setToast({type:"error",message:"Impossible de charger les documents fournisseurs."})}
 }
 useEffect(()=>{load()},[]);

 const lotMap=useMemo(()=>new Map(lots.map(l=>[l.id,l])),[lots]);
 const visible=useMemo(()=>{const t=search.toLowerCase().trim();return docs.filter(d=>!t||d.nom_fichier.toLowerCase().includes(t)||(d.reference_document??"").toLowerCase().includes(t)||labels[d.type_document].toLowerCase().includes(t)||(d.lot_beton_id?lotMap.get(d.lot_beton_id)?.reference_interne.toLowerCase().includes(t):false))},[docs,search,lotMap]);

 function toBase64(file:File){return new Promise<string>((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result).split(",",2)[1]??"");r.onerror=reject;r.readAsDataURL(file)})}

 async function upload(e:FormEvent){
  e.preventDefault();if(!form.file)return;
  if(form.file.size>15*1024*1024){setToast({type:"error",message:"Fichier limité à 15 Mo."});return}
  try{
   const contenu=await toBase64(form.file);
   const lot=lots.find(l=>l.id===Number(form.lot_beton_id));
   const r=await apiFetch(`${API}/api/documents-fournisseurs`,{
    method:"POST",headers:entetesAuthentifiees({"Content-Type":"application/json"}),
    body:JSON.stringify({
     type_document:form.type_document,nom_fichier:form.file.name,type_mime:form.file.type,
     contenu_base64:contenu,lot_beton_id:Number(form.lot_beton_id),article_id:lot?undefined:null,
     reference_document:form.reference_document||null,date_document:form.date_document||null,
     date_expiration:form.date_expiration||null,commentaire:form.commentaire||null
    })
   });
   const data=await r.json().catch(()=>null);if(!r.ok)throw new Error(data?.detail??"Dépôt impossible.");
   setModal(false);setForm({lot_beton_id:"",type_document:"CERTIFICAT",reference_document:"",date_document:"",date_expiration:"",commentaire:"",file:null});
   setToast({type:"success",message:"Document enregistré."});await load();
  }catch(e){setToast({type:"error",message:e instanceof Error?e.message:"Dépôt impossible."})}
 }

 async function openDoc(d:Doc){
  const r=await apiFetch(`${API}/api/documents-fournisseurs/${d.id}/fichier`,{headers:entetesAuthentifiees()});
  if(!r.ok){setToast({type:"error",message:"Document indisponible."});return}
  const blob=await r.blob();window.open(URL.createObjectURL(blob),"_blank","noopener,noreferrer");
 }
 async function del(d:Doc){
  if(!confirm(`Supprimer ${d.nom_fichier} ?`))return;
  const r=await apiFetch(`${API}/api/documents-fournisseurs/${d.id}`,{method:"DELETE",headers:entetesAuthentifiees()});
  if(!r.ok){setToast({type:"error",message:"Suppression impossible."});return}await load();
 }

 const incomplets=statuts.filter(s=>s.statut==="INCOMPLET").length,expires=statuts.filter(s=>s.statut==="EXPIRE").length,complets=statuts.filter(s=>s.statut==="COMPLET").length;
 return <div>
  <div className="breadcrumb">Qualité / Documents fournisseurs</div>
  <div className="page-heading page-heading-actions"><div><span className="eyebrow">Traçabilité documentaire</span><h1>Documents fournisseurs</h1><p>FDS obligatoires et pièces qualité rattachées aux lots béton.</p></div><Button onClick={()=>setModal(true)}><Plus size={17}/>Déposer un document</Button></div>
  <section className={styles.kpis}><article><FileCheck2/><span>Lots complets</span><strong>{complets}</strong></article><article><ShieldAlert/><span>Lots incomplets</span><strong>{incomplets}</strong></article><article><ShieldAlert/><span>Documents expirés</span><strong>{expires}</strong></article><article><FileText/><span>Documents</span><strong>{docs.length}</strong></article></section>
  <section className={styles.status}><h2>Conformité documentaire des lots béton</h2><div>{statuts.map(s=><article key={s.lot_id}><strong>{s.reference_interne}</strong><b className={styles.articleName}>{s.article_designation}</b><small className={styles.articleRef}>{s.article_reference}</small><span className={`${styles.badge} ${s.statut==="COMPLET"?styles.ok:s.statut==="EXPIRE"?styles.expired:styles.warn}`}>{s.statut}</span><small>FDS obligatoire {s.fds_presente?"✓":"✕"} · Certificat facultatif {s.certificat_present?"✓":"—"}</small></article>)}</div></section>
  <section className={styles.panel}><div className={styles.toolbar}><label className="search-field"><Search size={17}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Fichier, référence, type ou lot…"/></label></div><div className={styles.tableWrap}><table className={styles.table}><thead><tr><th>Document</th><th>Type</th><th>Lot</th><th>Référence</th><th>Date</th><th>Expiration</th><th>Taille</th><th/></tr></thead><tbody>{visible.map(d=><tr key={d.id}><td><button className={styles.link} onClick={()=>openDoc(d)}>{d.nom_fichier}</button></td><td>{labels[d.type_document]}</td><td>{d.lot_beton_id?lotMap.get(d.lot_beton_id)?.reference_interne??"—":"—"}</td><td>{d.reference_document??"—"}</td><td>{d.date_document??"—"}</td><td>{d.date_expiration??"—"}</td><td>{(d.taille_octets/1024).toLocaleString("fr-FR",{maximumFractionDigits:0})} Ko</td><td><button className={styles.trash} onClick={()=>del(d)}><Trash2 size={15}/></button></td></tr>)}{!visible.length&&<tr><td colSpan={8} className={styles.empty}>Aucun document.</td></tr>}</tbody></table></div></section>
  {modal&&<div className="modal-backdrop" style={{zIndex:10000}} onMouseDown={()=>setModal(false)}><section className="modal-card modal-card-wide" style={{position:"relative",zIndex:10001}} onMouseDown={e=>e.stopPropagation()}><div className="modal-header"><div><span className="eyebrow">Qualité fournisseur</span><h2>Déposer un document</h2></div></div><form className={styles.form} onSubmit={upload}><label>Lot béton *<select required value={form.lot_beton_id} onChange={e=>setForm({...form,lot_beton_id:e.target.value})}><option value="">Sélectionner…</option>{lots.map(l=><option key={l.id} value={l.id}>{l.reference_interne} — {l.article.reference} — {l.numero_lot_fournisseur}</option>)}</select></label><label>Type *<select value={form.type_document} onChange={e=>setForm({...form,type_document:e.target.value})}>{Object.entries(labels).map(([v,l])=><option key={v} value={v}>{String(l)}</option>)}</select></label><label>Référence document<input value={form.reference_document} onChange={e=>setForm({...form,reference_document:e.target.value})}/></label><label>Date document<input type="date" value={form.date_document} onChange={e=>setForm({...form,date_document:e.target.value})}/></label><label>Date expiration<input type="date" value={form.date_expiration} onChange={e=>setForm({...form,date_expiration:e.target.value})}/></label><label>Fichier PDF / image *<input required type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={(e:ChangeEvent<HTMLInputElement>)=>setForm({...form,file:e.target.files?.[0]??null})}/></label><label className={styles.wide}>Commentaire<textarea value={form.commentaire} onChange={e=>setForm({...form,commentaire:e.target.value})}/></label><div className={styles.actions}><Button type="submit">Enregistrer le document</Button></div></form></section></div>}
  {toast&&<Toast type={toast.type} message={toast.message} onClose={()=>setToast(null)}/>}
 </div>
}
