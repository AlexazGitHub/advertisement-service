from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app import models, schemas, crud
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advertisement Service")


@app.post("/advertisement", response_model=schemas.AdvertisementResponse)
def create_advertisement(advertisement: schemas.AdvertisementCreate, db: Session = Depends(get_db)):
    return crud.create_advertisement(db, advertisement)


@app.get("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def read_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    db_advertisement = crud.get_advertisement(db, advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement


@app.patch("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def update_advertisement(advertisement_id: int, advertisement: schemas.AdvertisementUpdate, db: Session = Depends(get_db)):
    db_advertisement = crud.update_advertisement(db, advertisement_id, advertisement)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement


@app.delete("/advertisement/{advertisement_id}")
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    db_advertisement = crud.delete_advertisement(db, advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"detail": "Advertisement deleted"}


@app.get("/advertisement", response_model=list[schemas.AdvertisementResponse])
def search_advertisements(
    title: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    author: Optional[str] = None,
    created_at_from: Optional[datetime] = None,
    created_at_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    return crud.search_advertisements(db, title, description, price, author, created_at_from, created_at_to)
