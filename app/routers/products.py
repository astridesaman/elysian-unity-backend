from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import SessionLocal
from .. import schemas, crud

router = APIRouter(prefix="/products", tags=["products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)):
    return crud.get_products(db)
