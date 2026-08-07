"use client";
import {FormEvent,useEffect,useMemo,useState} from "react";
import {Building2,PackageCheck,Plus,RefreshCcw,Search,ShoppingCart,Truck} from "lucide-react";
import {Button} from "@/components/ui/Button";
import {Toast} from "@/components/ui/Toast";
import {entetesAuthentifiees} from "@/lib/auth";
import styles from "./page.module.css";
const API=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8000";
type F={id:number;code:string;raison_sociale:string;contact:string|null;email:string|null;telephone:string|null;conditions_paiement:string|null;delai_habituel_jours:number|null;actif:boolean};
type A={id:number;reference:string;designation:string;unite:string};
type L={id:number;article_id:number;besoin_reapprovisionnement_id:number|null;reference_fournisseur:string|null;quantite_commandee:string;quantite_recue:string;prix_unitaire_ht:string;article:A};
type C={id:number;reference:string;fournisseur_id:number;statut:string;reference_fournisseur:string|null;date_livraison_prevue:string|null;commentaire:string|null;fournisseur:F;lignes:L[]};
type B={id:number;reference:string;article_id:number;quantite_demandee:string;quantite_commandee:string;quantite_recue:string;prix_unitaire_prevu:string|null;statut:string;article:A};
type E={id:number;code:string;nom:string};
const n=(x:any)=>Number(x??0); const eur=(x:number)=>new Intl.NumberFormat("fr-FR",{style:"currency",currency:"EUR"}).format(x);
export default function Achats(){
 const [tab,setTab]=useState<"commandes"|"fournisseurs">("commandes"),[fs,setFs]=useState<F[]>([]),[cs,setCs]=useState<C[]>([]),[bs,setBs]=useState<B[]>([]),[es,setEs]=useState<E[]>([]);
 const [toast,setToast]=useState<{type:"success"|"error";message:string}|null>(null),[modalF,setModalF]=useState(false),[modalC,setModalC]=useState(false),[editC,setEditC]=useState<C|null>(null),[reception,setReception]=useState<{c:C;l:L}|null>(null);
 const [ff,setFf]=useState({code:"",raison_sociale:"",contact:"",email:"",telephone:"",conditions_paiement:"",delai_habituel_jours:""});
 const [cf,setCf]=useState({fournisseur_id:"",besoins:[] as number[],date_livraison_prevue:"",commentaire:""});
 const [ef,setEf]=useState({statut:"BROUILLON",reference_fournisseur:"",date_livraison_prevue:"",commentaire:""});
 const [rf,setRf]=useState({quantite:"",emplacement_destination_id:"",prix_unitaire_ht:"",lot_id:"",commentaire:""});
 async function load(){try{const h=entetesAuthentifiees();const [a,b,c,d]=await Promise.all([fetch(`${API}/api/achats/fournisseurs`,{headers:h}),fetch(`${API}/api/achats/commandes`,{headers:h}),fetch(`${API}/api/reapprovisionnement/besoins`,{headers:h}),fetch(`${API}/api/emplacements`,{headers:h})]);if(!a.ok||!b.ok||!c.ok||!d.ok)throw 0;setFs(await a.json());setCs(await b.json());setBs(await c.json());setEs(await d.json())}catch{setToast({type:"error",message:"Impossible de charger le module achats."})}}
 useEffect(()=>{load()},[]);
 const ouverts=bs.filter(b=>["A_TRAITER","VALIDE"].includes(b.statut));
 async function creerF(e:FormEvent){
  e.preventDefault();
  try{
    const r=await fetch(`${API}/api/achats/fournisseurs`,{
      method:"POST",
      headers:entetesAuthentifiees({"Content-Type":"application/json"}),
      body:JSON.stringify({
        ...ff,
        delai_habituel_jours:ff.delai_habituel_jours
          ? Number(ff.delai_habituel_jours)
          : null
      })
    });
    const d=await r.json().catch(()=>null);
    if(!r.ok){
      setToast({
        type:"error",
        message:d?.detail??"Création impossible."
      });
      return;
    }
    setModalF(false);
    setFf({
      code:"",
      raison_sociale:"",
      contact:"",
      email:"",
      telephone:"",
      conditions_paiement:"",
      delai_habituel_jours:""
    });
    setToast({type:"success",message:"Fournisseur créé."});
    await load();
  }catch{
    setToast({
      type:"error",
      message:"Impossible de joindre le backend pour créer le fournisseur."
    });
  }
 }
 async function creerC(e:FormEvent){e.preventDefault();const selected=ouverts.filter(b=>cf.besoins.includes(b.id));if(!selected.length)return;const r=await fetch(`${API}/api/achats/commandes`,{method:"POST",headers:entetesAuthentifiees({"Content-Type":"application/json"}),body:JSON.stringify({fournisseur_id:Number(cf.fournisseur_id),date_livraison_prevue:cf.date_livraison_prevue||null,commentaire:cf.commentaire||null,lignes:selected.map(b=>({article_id:b.article_id,besoin_reapprovisionnement_id:b.id,quantite_commandee:n(b.quantite_demandee),prix_unitaire_ht:n(b.prix_unitaire_prevu),reference_fournisseur:null}))})});const d=await r.json().catch(()=>null);if(!r.ok){setToast({type:"error",message:d?.detail??"Commande impossible."});return}setModalC(false);setCf({fournisseur_id:"",besoins:[],date_livraison_prevue:"",commentaire:""});setToast({type:"success",message:`Commande ${d.reference} créée.`});load()}
 function ouvrirEdit(c:C){setEditC(c);setEf({statut:c.statut,reference_fournisseur:c.reference_fournisseur??"",date_livraison_prevue:c.date_livraison_prevue??"",commentaire:c.commentaire??""})}
 async function saveC(e:FormEvent){e.preventDefault();if(!editC)return;const r=await fetch(`${API}/api/achats/commandes/${editC.id}`,{method:"PATCH",headers:entetesAuthentifiees({"Content-Type":"application/json"}),body:JSON.stringify({...ef,date_livraison_prevue:ef.date_livraison_prevue||null,reference_fournisseur:ef.reference_fournisseur||null,commentaire:ef.commentaire||null})});const d=await r.json().catch(()=>null);if(!r.ok){setToast({type:"error",message:d?.detail??"Modification impossible."});return}setEditC(null);load()}
 function openR(c:C,l:L){setReception({c,l});setRf({quantite:String(n(l.quantite_commandee)-n(l.quantite_recue)),emplacement_destination_id:"",prix_unitaire_ht:l.prix_unitaire_ht,lot_id:"",commentaire:""})}
 async function recv(e:FormEvent){e.preventDefault();if(!reception)return;const r=await fetch(`${API}/api/achats/commandes/${reception.c.id}/lignes/${reception.l.id}/reception`,{method:"POST",headers:entetesAuthentifiees({"Content-Type":"application/json"}),body:JSON.stringify({quantite:n(rf.quantite),emplacement_destination_id:Number(rf.emplacement_destination_id),prix_unitaire_ht:n(rf.prix_unitaire_ht),lot_id:rf.lot_id?Number(rf.lot_id):null,commentaire:rf.commentaire||null})});const d=await r.json().catch(()=>null);if(!r.ok){setToast({type:"error",message:d?.detail??"Réception impossible."});return}setReception(null);setToast({type:"success",message:"Réception enregistrée : stock et CUMP mis à jour."});load()}
 const total=cs.filter(c=>c.statut!=="ANNULEE").reduce((s,c)=>s+c.lignes.reduce((x,l)=>x+n(l.quantite_commandee)*n(l.prix_unitaire_ht),0),0);
 return <div><div className="breadcrumb">Stocks / Fournisseurs & Achats</div><div className="page-heading page-heading-actions"><div><span className="eyebrow">Approvisionnement fournisseur</span><h1>Fournisseurs & Achats</h1><p>Regroupez les besoins du Lot L en commandes et réceptionnez-les dans le stock.</p></div><Button variant="secondary" onClick={load}><RefreshCcw size={17}/>Actualiser</Button></div>
 <div className={styles.kpis}><K icon={<Building2/>} l="Fournisseurs actifs" v={fs.filter(f=>f.actif).length}/><K icon={<ShoppingCart/>} l="Commandes ouvertes" v={cs.filter(c=>!["RECUE","ANNULEE"].includes(c.statut)).length}/><K icon={<Truck/>} l="À réceptionner" v={cs.filter(c=>["ENVOYEE","PARTIELLEMENT_RECUE"].includes(c.statut)).length}/><K icon={<PackageCheck/>} l="Montant commandes" v={eur(total)}/></div>
 <div className={styles.tabs}><button className={tab==="commandes"?styles.active:""} onClick={()=>setTab("commandes")}>Commandes</button><button className={tab==="fournisseurs"?styles.active:""} onClick={()=>setTab("fournisseurs")}>Fournisseurs</button></div>
 {tab==="fournisseurs"?<section className={styles.panel}><div className={styles.head}><h2>Référentiel fournisseurs</h2><Button onClick={()=>setModalF(true)}><Plus size={16}/>Nouveau fournisseur</Button></div><table><thead><tr><th>Code</th><th>Raison sociale</th><th>Contact</th><th>Email</th><th>Téléphone</th><th>Délai</th><th>Statut</th></tr></thead><tbody>{fs.map(f=><tr key={f.id}><td><strong>{f.code}</strong></td><td>{f.raison_sociale}</td><td>{f.contact??"—"}</td><td>{f.email??"—"}</td><td>{f.telephone??"—"}</td><td>{f.delai_habituel_jours!=null?`${f.delai_habituel_jours} j`:"—"}</td><td>{f.actif?"Actif":"Inactif"}</td></tr>)}</tbody></table></section>:
 <section className={styles.panel}><div className={styles.head}><div><h2>Commandes fournisseur</h2><small>{ouverts.length} besoin(s) du Lot L disponible(s)</small></div><Button onClick={()=>setModalC(true)} disabled={!ouverts.length||!fs.some(f=>f.actif)}><Plus size={16}/>Nouvelle commande</Button></div><table><thead><tr><th>Commande</th><th>Fournisseur</th><th>Lignes</th><th>Montant HT</th><th>Livraison prévue</th><th>Statut</th><th/></tr></thead><tbody>{cs.map(c=><tr key={c.id}><td><strong>{c.reference}</strong><br/><span>{c.reference_fournisseur??"—"}</span></td><td>{c.fournisseur.raison_sociale}</td><td>{c.lignes.length}</td><td>{eur(c.lignes.reduce((s,l)=>s+n(l.quantite_commandee)*n(l.prix_unitaire_ht),0))}</td><td>{c.date_livraison_prevue??"—"}</td><td><span className={styles.badge}>{c.statut.replaceAll("_"," ")}</span></td><td><div className={styles.actions}><button onClick={()=>ouvrirEdit(c)}>Éditer</button>{["VALIDEE","ENVOYEE","PARTIELLEMENT_RECUE"].includes(c.statut)&&c.lignes.filter(l=>n(l.quantite_recue)<n(l.quantite_commandee)).map(l=><button key={l.id} onClick={()=>openR(c,l)}>Réception {l.article.reference}</button>)}</div></td></tr>)}</tbody></table></section>}
 {modalF&&<M close={()=>setModalF(false)} title="Nouveau fournisseur"><form onSubmit={creerF} className={styles.form}><label>Code *<input required value={ff.code} onChange={e=>setFf({...ff,code:e.target.value})}/></label><label>Raison sociale *<input required value={ff.raison_sociale} onChange={e=>setFf({...ff,raison_sociale:e.target.value})}/></label><label>Contact<input value={ff.contact} onChange={e=>setFf({...ff,contact:e.target.value})}/></label><label>Email<input type="email" value={ff.email} onChange={e=>setFf({...ff,email:e.target.value})}/></label><label>Téléphone<input value={ff.telephone} onChange={e=>setFf({...ff,telephone:e.target.value})}/></label><label>Délai habituel (jours)<input type="number" min="0" value={ff.delai_habituel_jours} onChange={e=>setFf({...ff,delai_habituel_jours:e.target.value})}/></label><label>Conditions paiement<input value={ff.conditions_paiement} onChange={e=>setFf({...ff,conditions_paiement:e.target.value})}/></label><div className={styles.modalActions}><Button type="submit">Créer</Button></div></form></M>}
 {modalC&&<M close={()=>setModalC(false)} title="Nouvelle commande fournisseur"><form onSubmit={creerC} className={styles.form}><label>Fournisseur *<select required value={cf.fournisseur_id} onChange={e=>setCf({...cf,fournisseur_id:e.target.value})}><option value="">Sélectionner…</option>{fs.filter(f=>f.actif).map(f=><option key={f.id} value={f.id}>{f.code} — {f.raison_sociale}</option>)}</select></label><label>Livraison prévue<input type="date" value={cf.date_livraison_prevue} onChange={e=>setCf({...cf,date_livraison_prevue:e.target.value})}/></label><div className={styles.wide}><strong>Besoins à intégrer</strong>{ouverts.map(b=><label className={styles.need} key={b.id}><input type="checkbox" checked={cf.besoins.includes(b.id)} onChange={e=>setCf({...cf,besoins:e.target.checked?[...cf.besoins,b.id]:cf.besoins.filter(x=>x!==b.id)})}/><span>{b.reference} · {b.article.reference} · {b.article.designation}</span><b>{n(b.quantite_demandee)} {b.article.unite} · {eur(n(b.prix_unitaire_prevu))}/u</b></label>)}</div><label className={styles.wide}>Commentaire<textarea value={cf.commentaire} onChange={e=>setCf({...cf,commentaire:e.target.value})}/></label><div className={styles.modalActions}><Button type="submit" disabled={!cf.besoins.length}>Créer la commande</Button></div></form></M>}
 {editC&&<M close={()=>setEditC(null)} title={`Commande ${editC.reference}`}><form onSubmit={saveC} className={styles.form}><label>Statut<select value={ef.statut} onChange={e=>setEf({...ef,statut:e.target.value})}><option value="BROUILLON">Brouillon</option><option value="VALIDEE">Validée</option><option value="ENVOYEE">Envoyée</option><option value="ANNULEE">Annulée</option></select></label><label>Référence fournisseur<input value={ef.reference_fournisseur} onChange={e=>setEf({...ef,reference_fournisseur:e.target.value})}/></label><label>Livraison prévue<input type="date" value={ef.date_livraison_prevue} onChange={e=>setEf({...ef,date_livraison_prevue:e.target.value})}/></label><label className={styles.wide}>Commentaire<textarea value={ef.commentaire} onChange={e=>setEf({...ef,commentaire:e.target.value})}/></label><div className={styles.wide}>{editC.lignes.map(l=><div className={styles.line} key={l.id}><b>{l.article.reference}</b><span>{n(l.quantite_recue)} / {n(l.quantite_commandee)} {l.article.unite}</span><span>{eur(n(l.prix_unitaire_ht))}/u</span></div>)}</div><div className={styles.modalActions}><Button type="submit">Enregistrer</Button></div></form></M>}
 {reception&&<M close={()=>setReception(null)} title={`Réception ${reception.c.reference} — ${reception.l.article.reference}`}><form onSubmit={recv} className={styles.form}><label>Quantité *<input required inputMode="decimal" value={rf.quantite} onChange={e=>setRf({...rf,quantite:e.target.value})}/></label><label>Prix unitaire HT *<input required inputMode="decimal" value={rf.prix_unitaire_ht} onChange={e=>setRf({...rf,prix_unitaire_ht:e.target.value})}/></label><label>Emplacement *<select required value={rf.emplacement_destination_id} onChange={e=>setRf({...rf,emplacement_destination_id:e.target.value})}><option value="">Sélectionner…</option>{es.map(x=><option key={x.id} value={x.id}>{x.code} — {x.nom}</option>)}</select></label><label>Lot béton<input inputMode="numeric" placeholder="ID lot si béton" value={rf.lot_id} onChange={e=>setRf({...rf,lot_id:e.target.value})}/></label><label className={styles.wide}>Commentaire<textarea value={rf.commentaire} onChange={e=>setRf({...rf,commentaire:e.target.value})}/></label><div className={styles.modalActions}><Button type="submit">Enregistrer la réception</Button></div></form></M>}
 {toast&&<Toast type={toast.type} message={toast.message} onClose={()=>setToast(null)}/>}</div>
}
function K({icon,l,v}:{icon:React.ReactNode;l:string;v:any}){return <article className={styles.kpi}><div>{icon}</div><span>{l}</span><strong>{v}</strong></article>}
function M({close,title,children}:{close:()=>void;title:string;children:React.ReactNode}){return <div className="modal-backdrop" style={{zIndex:10000}} onMouseDown={close}><section className="modal-card modal-card-wide" style={{position:"relative",zIndex:10001}} onMouseDown={e=>e.stopPropagation()}><div className="modal-header"><div><span className="eyebrow">Achats fournisseurs</span><h2>{title}</h2></div></div>{children}</section></div>}
