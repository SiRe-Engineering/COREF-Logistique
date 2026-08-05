from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom_complet: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(
        String(180),
        unique=True,
        index=True,
    )
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), index=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    sessions = relationship(
        "SessionUtilisateur",
        back_populates="utilisateur",
        cascade="all, delete-orphan",
    )


class SessionUtilisateur(Base):
    __tablename__ = "sessions_utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"),
        index=True,
    )
    jeton_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
    )
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_expiration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    date_revocation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    utilisateur = relationship("Utilisateur", back_populates="sessions")
