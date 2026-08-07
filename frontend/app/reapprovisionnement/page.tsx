"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Check,
  CircleDollarSign,
  PackageCheck,
  RefreshCcw,
  Search,
  ShoppingCart,
  Truck,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";
import { entetesAuthentifiees } from "@/lib/auth";
import styles from "./page.module.css";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Article = {
  id:number; reference:string; designation:string; unite:string;
  stock_minimum:string; stock_maximum:string; seuil_alerte:string;
  dernier_prix_achat:string|null;
};
type Suggestion = {
  article:Article; quantite_physique:string; quantite_reservee:string;
  quantite_disponible:string; quantite_suggeree:string; niveau:string;
  besoin_ouvert_id:number|null;
};
type Besoin = {
  id:number; reference:string; article_id:number; quantite_suggeree:string;
  quantite_demandee:string; quantite_commandee:string; quantite_recue:string;
  prix_unitaire_prevu:string|null; fournisseur:string|null;
  reference_commande:string|null; statut:string; commentaire:string|null;
  article:Article;
};
type Emplacement={id:number;code:string;nom:string};
type Lot={id:number;article_id:number;reference_interne:string;numero_lot_fournisseur:string;actif:boolean};

function n(v:string|number|null|undefined){return Number(v??0)}
function q(v:string|number, unite:string){return `${n(v).toLocaleString("fr-FR",{maximumFractionDigits:3})} ${unite}`}
function euros(v:number){return new Intl.NumberFormat("fr-FR",{style:"currency",currency:"EUR"}).format(v)}

export default function ReapprovisionnementPage(){
  const [suggestions,setSuggestions]=useState<Suggestion[]>([]);
  const [besoins,setBesoins]=useState<Besoin[]>([]);
  const [emplacements,setEmplacements]=useState<Emplacement[]>([]);
  const [lots,setLots]=useState<Lot[]>([]);
  const [recherche,setRecherche]=useState("");
  const [filtre,setFiltre]=useState("OUVERTS");
  const [edition,setEdition]=useState<Besoin|null>(null);
  const [reception,setReception]=useState<Besoin|null>(null);
  const [form,setForm]=useState({quantite_demandee:"",quantite_commandee:"",prix_unitaire_prevu:"",fournisseur:"",reference_commande:"",statut:"A_TRAITER",commentaire:""});
  const [receptionForm,setReceptionForm]=useState({quantite:"",emplacement_destination_id:"",lot_id:"",prix_unitaire_ht:"",commentaire:""});
  const [toast,setToast]=useState<{type:"success"|"error";message:string}|null>(null);
  const [chargement,setChargement]=useState(true);

  async function charger(){
    setChargement(true);
    try{
      const headers=entetesAuthentifiees();
      const [s,b,e,l]=await Promise.all([
        fetch(`${API_URL}/api/reapprovisionnement/suggestions`,{headers}),
        fetch(`${API_URL}/api/reapprovisionnement/besoins`,{headers}),
        fetch(`${API_URL}/api/emplacements`,{headers}),
        fetch(`${API_URL}/api/lots-beton`,{headers}),
      ]);
      if(!s.ok||!b.ok||!e.ok||!l.ok) throw new Error();
      setSuggestions(await s.json()); setBesoins(await b.json());
      setEmplacements(await e.json()); setLots(await l.json());
    }catch{
      setToast({type:"error",message:"Impossible de charger le réapprovisionnement."});
    }finally{setChargement(false)}
  }
  useEffect(()=>{charger()},[]);

  const visibles=useMemo(()=>{
    const t=recherche.trim().toLowerCase();
    return besoins.filter(b=>{
      const ok=!t||b.reference.toLowerCase().includes(t)||b.article.reference.toLowerCase().includes(t)||b.article.designation.toLowerCase().includes(t)||(b.fournisseur??"").toLowerCase().includes(t);
      const statut=filtre==="TOUS"||filtre==="OUVERTS"&&["A_TRAITER","VALIDE","COMMANDE"].includes(b.statut)||b.statut===filtre;
      return ok&&statut;
    })
  },[besoins,recherche,filtre]);

  async function creer(s:Suggestion){
    const r=await fetch(`${API_URL}/api/reapprovisionnement/besoins`,{
      method:"POST",headers:entetesAuthentifiees({"Content-Type":"application/json"}),
      body:JSON.stringify({article_id:s.article.id,quantite_demandee:n(s.quantite_suggeree),prix_unitaire_prevu:s.article.dernier_prix_achat? n(s.article.dernier_prix_achat):null})
    });
    const d=await r.json().catch(()=>null);
    if(!r.ok){setToast({type:"error",message:d?.detail??"Création impossible."});return}
    setToast({type:"success",message:`Besoin ${d.reference} créé.`}); await charger();
  }

  function ouvrirEdition(b:Besoin){
    setEdition(b); setForm({
      quantite_demandee:b.quantite_demandee,quantite_commandee:b.quantite_commandee,
      prix_unitaire_prevu:b.prix_unitaire_prevu??"",fournisseur:b.fournisseur??"",
      reference_commande:b.reference_commande??"",statut:b.statut,commentaire:b.commentaire??""
    });
  }
  async function enregistrer(e:FormEvent){
    e.preventDefault(); if(!edition)return;
    const r=await fetch(`${API_URL}/api/reapprovisionnement/besoins/${edition.id}`,{
      method:"PATCH",headers:entetesAuthentifiees({"Content-Type":"application/json"}),
      body:JSON.stringify({
        quantite_demandee:n(form.quantite_demandee),quantite_commandee:n(form.quantite_commandee),
        prix_unitaire_prevu:form.prix_unitaire_prevu===""?null:n(form.prix_unitaire_prevu),
        fournisseur:form.fournisseur||null,reference_commande:form.reference_commande||null,
        statut:form.statut,commentaire:form.commentaire||null
      })
    });
    const d=await r.json().catch(()=>null);
    if(!r.ok){setToast({type:"error",message:d?.detail??"Modification impossible."});return}
    setEdition(null);setToast({type:"success",message:`${d.reference} mis à jour.`});await charger();
  }
  function ouvrirReception(b:Besoin){
    setReception(b); setReceptionForm({
      quantite:String(Math.max(0,n(b.quantite_commandee||b.quantite_demandee)-n(b.quantite_recue))),
      emplacement_destination_id:"",lot_id:"",prix_unitaire_ht:b.prix_unitaire_prevu??b.article.dernier_prix_achat??"",commentaire:""
    });
  }
  async function receptionner(e:FormEvent){
    e.preventDefault();if(!reception)return;
    const r=await fetch(`${API_URL}/api/reapprovisionnement/besoins/${reception.id}/reception`,{
      method:"POST",headers:entetesAuthentifiees({"Content-Type":"application/json"}),
      body:JSON.stringify({
        quantite:n(receptionForm.quantite),emplacement_destination_id:Number(receptionForm.emplacement_destination_id),
        lot_id:receptionForm.lot_id?Number(receptionForm.lot_id):null,
        prix_unitaire_ht:n(receptionForm.prix_unitaire_ht),commentaire:receptionForm.commentaire||null
      })
    });
    const d=await r.json().catch(()=>null);
    if(!r.ok){setToast({type:"error",message:d?.detail??"Réception impossible."});return}
    setReception(null);setToast({type:"success",message:"Réception enregistrée et stock mis à jour."});await charger();
  }

  const valeurOuverte=besoins.filter(b=>["A_TRAITER","VALIDE","COMMANDE"].includes(b.statut)).reduce((s,b)=>s+n(b.quantite_demandee)*n(b.prix_unitaire_prevu),0);

  return <div>
    <div className="breadcrumb">Stocks / Réapprovisionnement</div>
    <div className="page-heading page-heading-actions">
      <div><span className="eyebrow">Besoins d’achat</span><h1>Réapprovisionnement</h1><p>Transformez les seuils de stock en besoins, commandes et réceptions traçables.</p></div>
      <Button variant="secondary" onClick={charger}><RefreshCcw size={17}/>Actualiser</Button>
    </div>

    <section className={styles.metrics}>
      <Metric icon={<ShoppingCart/>} label="Suggestions" value={suggestions.length}/>
      <Metric icon={<Truck/>} label="Commandés" value={besoins.filter(b=>b.statut==="COMMANDE").length}/>
      <Metric icon={<PackageCheck/>} label="Réceptions terminées" value={besoins.filter(b=>b.statut==="RECU").length}/>
      <Metric icon={<CircleDollarSign/>} label="Valeur prévisionnelle ouverte" value={euros(valeurOuverte)}/>
    </section>

    <section className={styles.panel}>
      <div className={styles.panelHead}><div><span className="eyebrow">Calcul automatique</span><h2>Suggestions de réapprovisionnement</h2></div></div>
      <div className={styles.tableWrap}><table className={styles.table}><thead><tr><th>Article</th><th>Disponible</th><th>Mini</th><th>Maxi</th><th>Suggestion</th><th>Niveau</th><th/></tr></thead>
      <tbody>{suggestions.map(s=><tr key={s.article.id}><td><strong>{s.article.reference}</strong><br/><span>{s.article.designation}</span></td><td>{q(s.quantite_disponible,s.article.unite)}</td><td>{q(s.article.stock_minimum,s.article.unite)}</td><td>{n(s.article.stock_maximum)>0?q(s.article.stock_maximum,s.article.unite):<span className={styles.maxMissing}>Maxi à définir</span>}</td><td><strong>{q(s.quantite_suggeree,s.article.unite)}</strong></td><td><span className={`${styles.badge} ${s.niveau==="RUPTURE"?styles.danger:styles.warning}`}>{s.niveau==="RUPTURE"?"Rupture":"Sous seuil"}</span></td><td>{s.besoin_ouvert_id?<span className={styles.existing}>Besoin ouvert</span>:<Button onClick={()=>creer(s)}>Créer le besoin</Button>}</td></tr>)}
      {!chargement&&suggestions.length===0&&<tr><td colSpan={7} className={styles.empty}>Aucun réapprovisionnement suggéré.</td></tr>}</tbody></table></div>
    </section>

    <section className={styles.panel}>
      <div className={styles.toolbar}><label className="search-field"><Search size={17}/><input value={recherche} onChange={e=>setRecherche(e.target.value)} placeholder="Référence, article, fournisseur…"/></label>
      <select value={filtre} onChange={e=>setFiltre(e.target.value)}><option value="OUVERTS">Besoins ouverts</option><option value="A_TRAITER">À traiter</option><option value="VALIDE">Validés</option><option value="COMMANDE">Commandés</option><option value="RECU">Reçus</option><option value="ANNULE">Annulés</option><option value="TOUS">Tous</option></select></div>
      <div className={styles.tableWrap}><table className={styles.table}><thead><tr><th>Besoin</th><th>Article</th><th>Demandé</th><th>Commandé</th><th>Reçu</th><th>Fournisseur</th><th>Montant prévu</th><th>Statut</th><th/></tr></thead>
      <tbody>{visibles.map(b=><tr key={b.id}><td><strong>{b.reference}</strong><br/><span>{b.reference_commande??"—"}</span></td><td><strong>{b.article.reference}</strong><br/><span>{b.article.designation}</span></td><td>{q(b.quantite_demandee,b.article.unite)}</td><td>{q(b.quantite_commandee,b.article.unite)}</td><td>{q(b.quantite_recue,b.article.unite)}</td><td>{b.fournisseur??"—"}</td><td>{b.prix_unitaire_prevu?euros(n(b.quantite_demandee)*n(b.prix_unitaire_prevu)):"—"}</td><td><span className={styles.badge}>{b.statut.replaceAll("_"," ")}</span></td><td><div className={styles.actions}><button onClick={()=>ouvrirEdition(b)}>Éditer</button>{["VALIDE","COMMANDE"].includes(b.statut)&&<button onClick={()=>ouvrirReception(b)}>Réception</button>}</div></td></tr>)}</tbody></table></div>
    </section>

    {edition&&<div className="modal-backdrop" style={{zIndex:10000}} onMouseDown={()=>setEdition(null)}><section className="modal-card modal-card-wide" style={{position:"relative",zIndex:10001}} onMouseDown={e=>e.stopPropagation()}><div className="modal-header"><div><span className="eyebrow">Besoin d’achat</span><h2>{edition.reference}</h2><p>{edition.article.reference} — {edition.article.designation}</p></div></div>
      <form onSubmit={enregistrer}><div className="form-grid">
        <label className="field"><span>Quantité demandée</span><input required inputMode="decimal" value={form.quantite_demandee} onChange={e=>setForm({...form,quantite_demandee:e.target.value})}/></label>
        <label className="field"><span>Quantité commandée</span><input inputMode="decimal" value={form.quantite_commandee} onChange={e=>setForm({...form,quantite_commandee:e.target.value})}/></label>
        <label className="field"><span>Prix unitaire HT prévu</span><input inputMode="decimal" value={form.prix_unitaire_prevu} onChange={e=>setForm({...form,prix_unitaire_prevu:e.target.value})}/></label>
        <label className="field"><span>Fournisseur</span><input value={form.fournisseur} onChange={e=>setForm({...form,fournisseur:e.target.value})}/></label>
        <label className="field"><span>Référence commande</span><input value={form.reference_commande} onChange={e=>setForm({...form,reference_commande:e.target.value})}/></label>
        <label className="field"><span>Statut</span><select value={form.statut} onChange={e=>setForm({...form,statut:e.target.value})}><option value="A_TRAITER">À traiter</option><option value="VALIDE">Validé</option><option value="COMMANDE">Commandé</option><option value="ANNULE">Annulé</option></select></label>
        <label className="field field-wide"><span>Commentaire</span><textarea value={form.commentaire} onChange={e=>setForm({...form,commentaire:e.target.value})}/></label>
      </div><div className="modal-actions"><Button type="button" variant="ghost" onClick={()=>setEdition(null)}><X size={16}/>Annuler</Button><Button type="submit"><Check size={16}/>Enregistrer</Button></div></form>
    </section></div>}

    {reception&&<div className="modal-backdrop" style={{zIndex:10000}} onMouseDown={()=>setReception(null)}><section className="modal-card modal-card-wide" style={{position:"relative",zIndex:10001}} onMouseDown={e=>e.stopPropagation()}><div className="modal-header"><div><span className="eyebrow">Entrée de stock</span><h2>Réception {reception.reference}</h2><p>La réception créera un mouvement d’entrée et recalculera le CUMP.</p></div></div>
      <form onSubmit={receptionner}><div className="form-grid">
        <label className="field"><span>Quantité reçue *</span><input required inputMode="decimal" value={receptionForm.quantite} onChange={e=>setReceptionForm({...receptionForm,quantite:e.target.value})}/></label>
        <label className="field"><span>Prix unitaire HT *</span><input required inputMode="decimal" value={receptionForm.prix_unitaire_ht} onChange={e=>setReceptionForm({...receptionForm,prix_unitaire_ht:e.target.value})}/></label>
        <label className="field"><span>Emplacement destination *</span><select required value={receptionForm.emplacement_destination_id} onChange={e=>setReceptionForm({...receptionForm,emplacement_destination_id:e.target.value})}><option value="">Sélectionner…</option>{emplacements.map(x=><option key={x.id} value={x.id}>{x.code} — {x.nom}</option>)}</select></label>
        <label className="field"><span>Lot béton</span><select value={receptionForm.lot_id} onChange={e=>setReceptionForm({...receptionForm,lot_id:e.target.value})}><option value="">Aucun / non béton</option>{lots.filter(l=>l.article_id===reception.article_id&&l.actif).map(l=><option key={l.id} value={l.id}>{l.reference_interne} — {l.numero_lot_fournisseur}</option>)}</select><small>Obligatoire pour un article Béton.</small></label>
        <label className="field field-wide"><span>Commentaire réception</span><textarea value={receptionForm.commentaire} onChange={e=>setReceptionForm({...receptionForm,commentaire:e.target.value})}/></label>
      </div><div className="modal-actions"><Button type="button" variant="ghost" onClick={()=>setReception(null)}>Annuler</Button><Button type="submit"><PackageCheck size={16}/>Enregistrer la réception</Button></div></form>
    </section></div>}

    {toast&&<Toast type={toast.type} message={toast.message} onClose={()=>setToast(null)}/>}
  </div>
}
function Metric({icon,label,value}:{icon:React.ReactNode;label:string;value:string|number}){return <article className={styles.metric}><div>{icon}</div><span>{label}</span><strong>{value}</strong></article>}
