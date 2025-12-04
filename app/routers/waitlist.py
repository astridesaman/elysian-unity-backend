from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas, crud

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.WaitlistOut)
def add_to_waitlist(entry: schemas.WaitlistIn, db: Session = Depends(get_db)):
    return crud.create_waitlist_entry(db, entry)
