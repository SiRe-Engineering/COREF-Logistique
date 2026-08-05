from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True,
    )
    designation: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )
    famille: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    sous_famille: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    unite: Mapped[str] = mapped_column(
        String(30),
        default="unité",
    )
    stock_minimum: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        default=0,
    )
    actif: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
