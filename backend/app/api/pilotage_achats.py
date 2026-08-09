from collections import defaultdict
from datetime import date,timedelta
from decimal import Decimal
from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.orm import Session,selectinload
from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.achats import ArticleFournisseur,CommandeAchat,HistoriquePrixFournisseur
from app.models.article import Article
from app.models.utilisateur import Utilisateur
from app.schemas.pilotage_achats import *
router=APIRouter(prefix="/api/achats/pilotage",tags=["Pilotage achats"])
OUVERTS={"BROUILLON","VALIDEE","ENVOYEE","PARTIELLEMENT_RECUE"}
def montant(l):return l.quantite_commandee*(l.prix_unitaire_ht or Decimal("0"))
def reste(l):return max(l.quantite_commandee-l.quantite_recue,Decimal("0"))*(l.prix_unitaire_ht or Decimal("0"))
def late(c,today):return c.statut in {"ENVOYEE","PARTIELLEMENT_RECUE"} and c.date_livraison_prevue is not None and c.date_livraison_prevue<today
def retard_reel(c):
    if c.statut!="RECUE" or c.date_livraison_prevue is None or c.date_reception_finale is None:return None
    return max(0,(c.date_reception_finale.date()-c.date_livraison_prevue).days)
@router.get("",response_model=DashboardAchatsRead)
def dashboard(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    today=date.today();horizon=today+timedelta(days=30)
    cs=list(db.scalars(select(CommandeAchat).options(selectinload(CommandeAchat.lignes),selectinload(CommandeAchat.fournisseur)).order_by(CommandeAchat.date_creation.desc())).unique().all())
    ouverts=[c for c in cs if c.statut in OUVERTS];retardees=[c for c in ouverts if late(c,today)]
    prochaines=[
        c
        for c in ouverts
        if c.date_livraison_prevue is not None
        and (
            c.date_livraison_prevue < today
            or today <= c.date_livraison_prevue <= horizon
        )
    ]
    engage=sum((sum((reste(l) for l in c.lignes),Decimal("0")) for c in ouverts),Decimal("0"))
    retards=[CommandeAlerteRead(id=c.id,reference=c.reference,fournisseur=c.fournisseur.raison_sociale,statut=c.statut,date_livraison_prevue=c.date_livraison_prevue,jours_retard=(today-c.date_livraison_prevue).days,montant_restant_ht=sum((reste(l) for l in c.lignes),Decimal("0"))) for c in retardees]
    livraisons=[
        LivraisonAttendueRead(
            commande_id=c.id,
            reference=c.reference,
            fournisseur=c.fournisseur.raison_sociale,
            date_livraison_prevue=c.date_livraison_prevue,
            statut=c.statut,
            montant_restant_ht=sum(
                (reste(l) for l in c.lignes),
                Decimal("0"),
            ),
        )
        for c in prochaines
    ]
    livraisons.sort(
        key=lambda x: (
            0 if x.date_livraison_prevue < today else 1,
            x.date_livraison_prevue,
        )
    )
    st=defaultdict(lambda:{"f":None,"n":0,"m":Decimal("0"),"r":Decimal("0"),"late":0,"eval":0,"ok":0,"delays":[]})
    geval=gok=0
    for c in cs:
        x=st[c.fournisseur_id];x["f"]=c.fournisseur;x["n"]+=1;x["m"]+=sum((montant(l) for l in c.lignes),Decimal("0"))
        if c.statut in OUVERTS:x["r"]+=sum((reste(l) for l in c.lignes),Decimal("0"))
        if late(c,today):x["late"]+=1
        rr=retard_reel(c)
        if rr is not None:
            x["eval"]+=1;geval+=1;x["delays"].append(rr)
            if rr==0:x["ok"]+=1;gok+=1
    fs=[]
    for x in st.values():
        f=x["f"];otd=(Decimal(x["ok"])/Decimal(x["eval"])*Decimal("100")).quantize(Decimal("0.1")) if x["eval"] else None
        avg=(sum(Decimal(v) for v in x["delays"])/Decimal(len(x["delays"]))).quantize(Decimal("0.1")) if x["delays"] else None
        fs.append(PerformanceFournisseurRead(fournisseur_id=f.id,code=f.code,raison_sociale=f.raison_sociale,commandes=x["n"],commandes_evaluees_otd=x["eval"],commandes_a_lheure=x["ok"],otd_pct=otd,retard_moyen_jours=avg,montant_commande_ht=x["m"],montant_restant_ht=x["r"],commandes_en_retard=x["late"]))
    liens=list(db.scalars(select(ArticleFournisseur).options(selectinload(ArticleFournisseur.article),selectinload(ArticleFournisseur.fournisseur))).unique().all())
    evol=[]
    for l in liens:
        h=list(db.scalars(select(HistoriquePrixFournisseur).where(HistoriquePrixFournisseur.article_fournisseur_id==l.id).order_by(HistoriquePrixFournisseur.date_effet.desc(),HistoriquePrixFournisseur.id.desc()).limit(2)).all())
        act=h[0].prix_unitaire_ht if h else l.prix_unitaire_ht;prev=h[1].prix_unitaire_ht if len(h)>1 else None
        var=((act-prev)/prev*Decimal("100")).quantize(Decimal("0.1")) if act is not None and prev not in (None,0) else None
        evol.append(EvolutionPrixRead(article_fournisseur_id=l.id,article_reference=l.article.reference,article_designation=l.article.designation,fournisseur_code=l.fournisseur.code,fournisseur=l.fournisseur.raison_sociale,prix_actuel=act,prix_precedent=prev,variation_pct=var,date_dernier_prix=h[0].date_effet if h else l.date_maj_prix))
    by=defaultdict(list)
    for l in liens:by[l.article_id].append(l)
    crit=[];sf=stf=0
    for art in db.scalars(select(Article).where(Article.actif.is_(True)).order_by(Article.reference)).all():
        ls=by.get(art.id,[]);pref=next((l for l in ls if l.fournisseur_prefere),None);tar=pref or (ls[0] if ls else None);an=[]
        if not ls:sf+=1;an.append("Aucun fournisseur")
        if ls and not pref:an.append("Aucun fournisseur préféré")
        if tar is None or tar.prix_unitaire_ht is None:stf+=1;an.append("Aucun tarif")
        if tar is not None and tar.delai_jours is None:an.append("Délai non renseigné")
        if an:crit.append(ArticleCritiqueRead(article_id=art.id,reference=art.reference,designation=art.designation,fournisseur_prefere=pref.fournisseur.raison_sociale if pref else None,prix_unitaire_ht=tar.prix_unitaire_ht if tar else None,delai_jours=tar.delai_jours if tar else None,anomalies=an))
    ecarts=[]
    for c in cs:
        if c.statut!="RECUE":continue
        for l in c.lignes:
            e=l.quantite_recue-l.quantite_commandee
            if e!=0:ecarts.append(EcartReceptionRead(commande_id=c.id,commande_reference=c.reference,fournisseur=c.fournisseur.raison_sociale,article_reference=l.article.reference,article_designation=l.article.designation,quantite_commandee=l.quantite_commandee,quantite_recue=l.quantite_recue,ecart_quantite=e,unite=l.article.unite,date_reception_finale=c.date_reception_finale))
    otd=(Decimal(gok)/Decimal(geval)*Decimal("100")).quantize(Decimal("0.1")) if geval else None
    return DashboardAchatsRead(kpis=KpiAchatsRead(commandes_ouvertes=len(ouverts),commandes_en_retard=len(retardees),livraisons_30_jours=len(prochaines),montant_engage_ht=engage,articles_sans_fournisseur=sf,articles_sans_tarif=stf,otd_global_pct=otd),retards=retards[:50],livraisons=livraisons[:50],fournisseurs=fs,prix=evol[:100],articles_critiques=crit[:100],ecarts_reception=ecarts[:100])

@router.get("/qualite-fournisseurs")
def qualite_fournisseurs(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    from app.models.non_conformite_fournisseur import NonConformiteFournisseur
    from app.models.reception_achat import ReceptionAchat
    receptions=list(db.scalars(select(ReceptionAchat)).unique().all())
    ncfs=list(db.scalars(select(NonConformiteFournisseur)).unique().all())
    stats=defaultdict(lambda:{"fournisseur":"","receptions":0,"ncf":0,"ouvertes":0})
    for r in receptions:
        x=stats[r.commande.fournisseur_id];x["fournisseur"]=r.commande.fournisseur.raison_sociale;x["receptions"]+=1
    for n in ncfs:
        fid=n.reception.commande.fournisseur_id;x=stats[fid];x["fournisseur"]=n.reception.commande.fournisseur.raison_sociale;x["ncf"]+=1
        if n.statut!="CLOTUREE":x["ouvertes"]+=1
    return [{"fournisseur_id":fid,**x,"taux_ncf_pct":round(x["ncf"]/x["receptions"]*100,1) if x["receptions"] else 0} for fid,x in stats.items()]
