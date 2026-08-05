from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MovementType(str, Enum):
    ENTRY = "entry"
    EXIT = "exit"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    designation: Mapped[str] = mapped_column(String(255), index=True)
    family: Mapped[str | None] = mapped_column(String(120), nullable=True)
    subfamily: Mapped[str | None] = mapped_column(String(120), nullable=True)
    unit: Mapped[str] = mapped_column(String(30), default="unité")
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    source_location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    destination_location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    movement_type: Mapped[MovementType] = mapped_column(SqlEnum(MovementType))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    reason: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    item: Mapped[Item] = relationship()
    source_location: Mapped[Location | None] = relationship(foreign_keys=[source_location_id])
    destination_location: Mapped[Location | None] = relationship(foreign_keys=[destination_location_id])
