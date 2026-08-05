from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Emplacement(Base):
    __tablename__ = "emplacements"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    nom: Mapped[str] = mapped_column(String(150))
    type: Mapped[str] = mapped_column(String(30), index=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    allee: Mapped[str | None] = mapped_column(String(5), nullable=True)
    rack: Mapped[str | None] = mapped_column(String(10), nullable=True)
    etage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    case: Mapped[str | None] = mapped_column(String(5), nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    parent: Mapped["Emplacement | None"] = relationship(
        remote_side="Emplacement.id",
        back_populates="enfants",
    )
    enfants: Mapped[list["Emplacement"]] = relationship(
        back_populates="parent",
        order_by="Emplacement.code",
    )
