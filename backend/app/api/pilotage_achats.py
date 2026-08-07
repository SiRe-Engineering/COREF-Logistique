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
@router.get("",response_model=DashboardAchatsRead)
def dashboard(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    today=date.today();horizon=today+timedelta(days=30)
    cs=list(db.scalars(select(CommandeAchat).options(selectinload(CommandeAchat.lignes),selectinload(CommandeAchat.fournisseur)).order_by(CommandeAchat.date_creation.desc())).unique().all())
    ouverts=[c for c in cs if c.statut in OUVERTS]
    def late(c):return c.statut in {"ENVOYEE","PARTIELLEMENT_RECUE"} and c.date_livraison_prevue is not None and c.date_livraison_prevue<today
    retardees=[c for c in ouverts if late(c)];prochaines=[c for c in ouverts if c.date_livraison_prevue is not None and today<=c.date_livraison_prevue<=horizon]
    engage=sum((sum((reste(l) for l in c.lignes),Decimal("0")) for c in ouverts),Decimal("0"))
    retards=[CommandeAlerteRead(id=c.id,reference=c.reference,fournisseur=c.fournisseur.raison_sociale,statut=c.statut,date_livraison_prevue=c.date_livraison_prevue,jours_retard=(today-c.date_livraison_prevue).days,montant_restant_ht=sum((reste(l) for l in c.lignes),Decimal("0"))) for c in retardees];retards.sort(key=lambda x:x.jours_retard,reverse=True)
    livraisons=[LivraisonAttendueRead(commande_id=c.id,reference=c.reference,fournisseur=c.fournisseur.raison_sociale,date_livraison_prevue=c.date_livraison_prevue,statut=c.statut,montant_restant_ht=sum((reste(l) for l in c.lignes),Decimal("0"))) for c in prochaines];livraisons.sort(key=lambda x:x.date_livraison_prevue)
    st=defaultdict(lambda:{"f":None,"n":0,"m":Decimal("0"),"r":Decimal("0"),"late":0,"ev":0,"ok":0})
    for c in cs:
        s=st[c.fournisseur_id];s["f"]=c.fournisseur;s["n"]+=1;s["m"]+=sum((montant(l) for l in c.lignes),Decimal("0"))
        if c.statut in OUVERTS:s["r"]+=sum((reste(l) for l in c.lignes),Decimal("0"))
        if late(c):s["late"]+=1
        if c.date_livraison_prevue:
            if c.statut=="RECUE":s["ev"]+=1;s["ok"]+=1
            elif late(c):s["ev"]+=1
    fs=[]
    for s in st.values():
        f=s["f"];t=(Decimal(s["ok"])/Decimal(s["ev"])*Decimal("100")).quantize(Decimal("0.1")) if s["ev"] else None
        fs.append(PerformanceFournisseurRead(fournisseur_id=f.id,code=f.code,raison_sociale=f.raison_sociale,commandes=s["n"],montant_commande_ht=s["m"],montant_restant_ht=s["r"],commandes_en_retard=s["late"],taux_service_indicatif=t))
    fs.sort(key=lambda x:(x.commandes_en_retard,x.montant_restant_ht),reverse=True)
    liens=list(db.scalars(select(ArticleFournisseur).options(selectinload(ArticleFournisseur.article),selectinload(ArticleFournisseur.fournisseur))).unique().all());evol=[]
    for l in liens:
        h=list(db.scalars(select(HistoriquePrixFournisseur).where(HistoriquePrixFournisseur.article_fournisseur_id==l.id).order_by(HistoriquePrixFournisseur.date_effet.desc(),HistoriquePrixFournisseur.id.desc()).limit(2)).all())
        a=h[0].prix_unitaire_ht if h else l.prix_unitaire_ht;p=h[1].prix_unitaire_ht if len(h)>1 else None;v=((a-p)/p*Decimal("100")).quantize(Decimal("0.1")) if a is not None and p not in (None,0) else None
        evol.append(EvolutionPrixRead(article_fournisseur_id=l.id,article_reference=l.article.reference,article_designation=l.article.designation,fournisseur_code=l.fournisseur.code,fournisseur=l.fournisseur.raison_sociale,prix_actuel=a,prix_precedent=p,variation_pct=v,date_dernier_prix=h[0].date_effet if h else l.date_maj_prix))
    evol.sort(key=lambda x:abs(x.variation_pct or Decimal("0")),reverse=True)
    by=defaultdict(list)
    for l in liens:by[l.article_id].append(l)
    crit=[];sf=0;stf=0
    for a in db.scalars(select(Article).where(Article.actif.is_(True)).order_by(Article.reference)).all():
        ls=by.get(a.id,[]);pref=next((l for l in ls if l.fournisseur_prefere),None);tar=pref or (ls[0] if ls else None);an=[]
        if not ls:sf+=1;an.append("Aucun fournisseur")
        if ls and not pref:an.append("Aucun fournisseur préféré")
        if tar is None or tar.prix_unitaire_ht is None:stf+=1;an.append("Aucun tarif")
        if tar is not None and tar.delai_jours is None:an.append("Délai non renseigné")
        if an:crit.append(ArticleCritiqueRead(article_id=a.id,reference=a.reference,designation=a.designation,fournisseur_prefere=pref.fournisseur.raison_sociale if pref else None,prix_unitaire_ht=tar.prix_unitaire_ht if tar else None,delai_jours=tar.delai_jours if tar else None,anomalies=an))
    return DashboardAchatsRead(kpis=KpiAchatsRead(commandes_ouvertes=len(ouverts),commandes_en_retard=len(retardees),livraisons_30_jours=len(prochaines),montant_engage_ht=engage,articles_sans_fournisseur=sf,articles_sans_tarif=stf),retards=retards[:50],livraisons=livraisons[:50],fournisseurs=fs,prix=evol[:100],articles_critiques=crit[:100])
