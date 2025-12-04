from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas, crud

router = APIRouter(prefix="/orders", tags=["orders"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.OrderOut)
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    try:
        order = crud.create_order(db, order_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return order


@router.get("/", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)
