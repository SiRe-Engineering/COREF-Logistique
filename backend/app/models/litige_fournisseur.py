from datetime import date,datetime
from decimal import Decimal
from sqlalchemy import Date,DateTime,ForeignKey,Numeric,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
class LitigeFournisseur(Base):
    __tablename__="litiges_fournisseurs"
    id:Mapped[int]=mapped_column(primary_key=True)
    reference:Mapped[str]=mapped_column(String(30),unique=True)
    ncf_id:Mapped[int]=mapped_column(ForeignKey("non_conformites_fournisseurs.id",ondelete="RESTRICT"),unique=True)
    type_traitement:Mapped[str]=mapped_column(String(40))
    statut:Mapped[str]=mapped_column(String(40),index=True)
    quantite_retour:Mapped[Decimal|None]=mapped_column(Numeric(14,3),nullable=True)
    emplacement_source_id:Mapped[int|None]=mapped_column(ForeignKey("emplacements.id",ondelete="RESTRICT"),nullable=True)
    date_retour:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    mouvement_sortie_id:Mapped[int|None]=mapped_column(ForeignKey("mouvements_stock.id",ondelete="SET NULL"),nullable=True)
    reference_avoir:Mapped[str|None]=mapped_column(String(120),nullable=True)
    montant_avoir_ht:Mapped[Decimal|None]=mapped_column(Numeric(14,2),nullable=True)
    date_avoir:Mapped[date|None]=mapped_column(Date,nullable=True)
    reception_remplacement_id:Mapped[int|None]=mapped_column(ForeignKey("receptions_achat.id",ondelete="SET NULL"),nullable=True)
    quantite_conforme_tri:Mapped[Decimal|None]=mapped_column(Numeric(14,3),nullable=True)
    quantite_rebut_tri:Mapped[Decimal|None]=mapped_column(Numeric(14,3),nullable=True)
    commentaire:Mapped[str|None]=mapped_column(Text,nullable=True)
    date_creation:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    date_cloture:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    cree_par:Mapped[str|None]=mapped_column(String(150),nullable=True)
    ncf=relationship("NonConformiteFournisseur",lazy="joined")
    emplacement_source=relationship("Emplacement",lazy="joined")
    reception_remplacement=relationship("ReceptionAchat",foreign_keys=[reception_remplacement_id],lazy="joined")
