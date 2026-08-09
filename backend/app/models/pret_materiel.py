from datetime import date,datetime
from sqlalchemy import Date,DateTime,ForeignKey,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base

class PretMateriel(Base):
    __tablename__="prets_materiel"

    id:Mapped[int]=mapped_column(primary_key=True)
    reference:Mapped[str]=mapped_column(String(30),unique=True)
    materiel_id:Mapped[int]=mapped_column(ForeignKey("materiels.id",ondelete="RESTRICT"),index=True)
    emprunteur_id:Mapped[int|None]=mapped_column(ForeignKey("utilisateurs.id",ondelete="SET NULL"),nullable=True)
    affaire_id:Mapped[int|None]=mapped_column(ForeignKey("affaires.id",ondelete="SET NULL"),nullable=True)
    site_zone:Mapped[str|None]=mapped_column(String(180),nullable=True)
    date_sortie:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    date_retour_prevue:Mapped[date]=mapped_column(Date)
    date_retour_reelle:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    etat_depart:Mapped[str]=mapped_column(String(30))
    etat_retour:Mapped[str|None]=mapped_column(String(30),nullable=True)
    emplacement_depart_id:Mapped[int|None]=mapped_column(ForeignKey("emplacements.id",ondelete="SET NULL"),nullable=True)
    emplacement_retour_id:Mapped[int|None]=mapped_column(ForeignKey("emplacements.id",ondelete="SET NULL"),nullable=True)
    commentaire_sortie:Mapped[str|None]=mapped_column(Text,nullable=True)
    commentaire_retour:Mapped[str|None]=mapped_column(Text,nullable=True)
    cree_par:Mapped[str|None]=mapped_column(String(150),nullable=True)

    materiel=relationship("Materiel",lazy="joined")
    emprunteur=relationship("Utilisateur",foreign_keys=[emprunteur_id],lazy="joined")
    affaire=relationship("Affaire",lazy="joined")
    emplacement_depart=relationship("Emplacement",foreign_keys=[emplacement_depart_id],lazy="joined")
    emplacement_retour=relationship("Emplacement",foreign_keys=[emplacement_retour_id],lazy="joined")
