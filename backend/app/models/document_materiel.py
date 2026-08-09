from datetime import date,datetime
from sqlalchemy import Date,DateTime,ForeignKey,Integer,LargeBinary,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
class DocumentMateriel(Base):
    __tablename__="documents_materiel"
    id:Mapped[int]=mapped_column(primary_key=True)
    materiel_id:Mapped[int]=mapped_column(ForeignKey("materiels.id",ondelete="CASCADE"),index=True)
    type_document:Mapped[str]=mapped_column(String(50));nom_fichier:Mapped[str]=mapped_column(String(255))
    type_mime:Mapped[str]=mapped_column(String(100));taille_octets:Mapped[int]=mapped_column(Integer)
    contenu:Mapped[bytes]=mapped_column(LargeBinary)
    reference_document:Mapped[str|None]=mapped_column(String(150),nullable=True)
    date_document:Mapped[date|None]=mapped_column(Date,nullable=True)
    date_expiration:Mapped[date|None]=mapped_column(Date,nullable=True,index=True)
    organisme:Mapped[str|None]=mapped_column(String(180),nullable=True)
    commentaire:Mapped[str|None]=mapped_column(Text,nullable=True)
    date_depot:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    depose_par:Mapped[str|None]=mapped_column(String(150),nullable=True)
    materiel=relationship("Materiel",lazy="joined")
