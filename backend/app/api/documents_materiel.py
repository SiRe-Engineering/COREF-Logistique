import base64,binascii
from datetime import date,timedelta
from fastapi import APIRouter,Depends,HTTPException,Response,status
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.document_materiel import DocumentMateriel
from app.models.materiel import Materiel
from app.models.utilisateur import Utilisateur

router=APIRouter(prefix="/api/documents-materiel",tags=["Documents matériel"])
MAX=15*1024*1024
MIMES={"application/pdf","image/png","image/jpeg","image/webp"}
TYPES={"CONTROLE","CERTIFICAT","NOTICE","RAPPORT","ETALONNAGE","ASSURANCE","AUTRE"}

class Create(BaseModel):
    materiel_id:int;type_document:str;nom_fichier:str=Field(min_length=1,max_length=255)
    type_mime:str;contenu_base64:str;reference_document:str|None=None
    date_document:date|None=None;date_expiration:date|None=None;organisme:str|None=None;commentaire:str|None=None

def decode(v):
    if "," in v and v.lstrip().startswith("data:"):v=v.split(",",1)[1]
    try:b=base64.b64decode(v,validate=True)
    except (ValueError,binascii.Error) as e:raise HTTPException(422,"Contenu du fichier invalide.") from e
    if not b:raise HTTPException(422,"Le fichier est vide.")
    if len(b)>MAX:raise HTTPException(413,"Le fichier dépasse 15 Mo.")
    return b

def serial(x):
    t=date.today()
    st="SANS_ECHEANCE" if not x.date_expiration else "EXPIRE" if x.date_expiration<t else "A_ECHEANCE" if x.date_expiration<=t+timedelta(days=30) else "VALIDE"
    return {"id":x.id,"materiel_id":x.materiel_id,"numero_inventaire":x.materiel.numero_inventaire,"designation":x.materiel.designation,
      "type_document":x.type_document,"nom_fichier":x.nom_fichier,"type_mime":x.type_mime,"taille_octets":x.taille_octets,
      "reference_document":x.reference_document,"date_document":x.date_document,"date_expiration":x.date_expiration,
      "organisme":x.organisme,"commentaire":x.commentaire,"date_depot":x.date_depot,"depose_par":x.depose_par,"statut":st}

@router.get("")
def liste(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    return [serial(x) for x in db.scalars(select(DocumentMateriel).order_by(DocumentMateriel.date_depot.desc())).unique().all()]

@router.get("/dashboard")
def dashboard(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    rows=[serial(x) for x in db.scalars(select(DocumentMateriel)).unique().all()]
    return {"documents":len(rows),"expires":sum(x["statut"]=="EXPIRE" for x in rows),"a_echeance":sum(x["statut"]=="A_ECHEANCE" for x in rows),"materiels_documentes":len({x["materiel_id"] for x in rows})}

@router.post("",status_code=status.HTTP_201_CREATED)
def deposer(p:Create,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    if p.type_document not in TYPES:raise HTTPException(422,"Type de document invalide.")
    if p.type_mime not in MIMES:raise HTTPException(422,"Formats autorisés : PDF, PNG, JPG/JPEG, WEBP.")
    m=db.get(Materiel,p.materiel_id)
    if not m or not m.actif:raise HTTPException(404,"Matériel introuvable.")
    b=decode(p.contenu_base64)
    x=DocumentMateriel(materiel_id=p.materiel_id,type_document=p.type_document,nom_fichier=p.nom_fichier,
      type_mime=p.type_mime,taille_octets=len(b),contenu=b,reference_document=p.reference_document,
      date_document=p.date_document,date_expiration=p.date_expiration,organisme=p.organisme,
      commentaire=p.commentaire,depose_par=u.nom_complet)
    db.add(x);db.commit();db.refresh(x);return serial(x)

@router.get("/{id}/fichier")
def fichier(id:int,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    x=db.get(DocumentMateriel,id)
    if not x:raise HTTPException(404,"Document introuvable.")
    nom=x.nom_fichier.replace('"',"")
    return Response(content=x.contenu,media_type=x.type_mime,headers={"Content-Disposition":f'inline; filename="{nom}"',"Cache-Control":"private, max-age=3600"})

@router.delete("/{id}",status_code=204)
def supprimer(id:int,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    x=db.get(DocumentMateriel,id)
    if not x:raise HTTPException(404,"Document introuvable.")
    db.delete(x);db.commit()
