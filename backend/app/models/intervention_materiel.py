from datetime import date,datetime
from decimal import Decimal
from sqlalchemy import Date,DateTime,ForeignKey,Numeric,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base

class InterventionMateriel(Base):
    __tablename__="interventions_materiel"
    id:Mapped[int]=mapped_column(primary_key=True)
    reference:Mapped[str]=mapped_column(String(30),unique=True)
    materiel_id:Mapped[int]=mapped_column(ForeignKey("materiels.id",ondelete="RESTRICT"),index=True)
    type_intervention:Mapped[str]=mapped_column(String(40))
    statut:Mapped[str]=mapped_column(String(30),index=True)
    date_signalement:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    date_planifiee:Mapped[date|None]=mapped_column(Date,nullable=True)
    date_debut:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    date_fin:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    description:Mapped[str]=mapped_column(Text)
    diagnostic:Mapped[str|None]=mapped_column(Text,nullable=True)
    action_realisee:Mapped[str|None]=mapped_column(Text,nullable=True)
    prestataire:Mapped[str|None]=mapped_column(String(180),nullable=True)
    cout_ht:Mapped[Decimal|None]=mapped_column(Numeric(14,2),nullable=True)
    prochain_controle:Mapped[date|None]=mapped_column(Date,nullable=True)
    cree_par:Mapped[str|None]=mapped_column(String(150),nullable=True)
    materiel=relationship("Materiel",lazy="joined")
