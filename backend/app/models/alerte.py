from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AlerteLogistique(Base):
    __tablename__ = "alertes_logistiques"

    id: Mapped[int] = mapped_column(primary_key=True)
    cle: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    categorie: Mapped[str] = mapped_column(String(40), index=True)
    niveau: Mapped[str] = mapped_column(String(20), index=True)
    titre: Mapped[str] = mapped_column(String(180))
    message: Mapped[str] = mapped_column(Text)
    lien: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    statut: Mapped[str] = mapped_column(
        String(20),
        default="ACTIVE",
        index=True,
    )
    date_premiere_detection: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_derniere_detection: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_resolution: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    acquittee_par: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    date_acquittement: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
