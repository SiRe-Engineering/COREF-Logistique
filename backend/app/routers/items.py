from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Item
from app.schemas import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/api/items", tags=["Articles"])


@router.get("", response_model=list[ItemRead])
def list_items(
    search: str | None = Query(default=None, max_length=100),
    active_only: bool = True,
    db: Session = Depends(get_db),
) -> list[Item]:
    statement = select(Item).order_by(Item.reference)
    if active_only:
        statement = statement.where(Item.is_active.is_(True))
    if search:
        term = f"%{search.strip()}%"
        statement = statement.where(
            or_(Item.reference.ilike(term), Item.designation.ilike(term))
        )
    return list(db.scalars(statement).all())


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> Item:
    item = Item(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cette référence existe déjà.")
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Article introuvable.")
    return item


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
) -> Item:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    data = payload.model_dump(exclude_unset=True)
    if "reference" in data and data["reference"]:
        data["reference"] = data["reference"].strip().upper()

    for key, value in data.items():
        setattr(item, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cette référence existe déjà.")
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_item(item_id: int, db: Session = Depends(get_db)) -> None:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Article introuvable.")
    item.is_active = False
    db.commit()
