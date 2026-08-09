from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime,ForeignKey,Numeric,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base

class NonConformiteFournisseur(Base):
    __tablename__="non_conformites_fournisseurs"
    id:Mapped[int]=mapped_column(primary_key=True)
    reference:Mapped[str]=mapped_column(String(30),unique=True)
    reception_id:Mapped[int]=mapped_column(ForeignKey("receptions_achat.id",ondelete="RESTRICT"),index=True)
    quantite_concernee:Mapped[Decimal]=mapped_column(Numeric(14,3))
    description:Mapped[str]=mapped_column(Text)
    decision:Mapped[str|None]=mapped_column(String(40),nullable=True)
    responsable:Mapped[str|None]=mapped_column(String(150),nullable=True)
    statut:Mapped[str]=mapped_column(String(30),default="OUVERTE",index=True)
    commentaire_traitement:Mapped[str|None]=mapped_column(Text,nullable=True)
    date_creation:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    date_cloture:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    cree_par:Mapped[str|None]=mapped_column(String(150),nullable=True)
    reception=relationship("ReceptionAchat",lazy="joined")

NonConformiteFournisseur.litiges=relationship("LitigeFournisseur",lazy="selectin",viewonly=True)
