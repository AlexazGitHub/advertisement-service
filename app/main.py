from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, crud, auth
from app.database import engine, get_db
from app.dependencies import get_current_user_optional, get_current_user_required

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advertisement Service")


# ---------- Auth ----------

@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, credentials.username)
    if user is None or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# ---------- Users ----------

@app.post("/user", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user.username)
    if existing is not None:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)


@app.get("/user/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.patch("/user/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_required),
):
    if current_user.group != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_user = crud.update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/user/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_required),
):
    if current_user.group != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_user = crud.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}


# ---------- Advertisements ----------

@app.post("/advertisement", response_model=schemas.AdvertisementResponse)
def create_advertisement(
    advertisement: schemas.AdvertisementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_required),
):
    return crud.create_advertisement(db, advertisement, owner_id=current_user.id)


@app.get("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def read_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    db_advertisement = crud.get_advertisement(db, advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement


@app.patch("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def update_advertisement(
    advertisement_id: int,
    advertisement: schemas.AdvertisementUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_required),
):
    db_advertisement = crud.get_advertisement(db, advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if current_user.group != "admin" and db_advertisement.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_advertisement(db, advertisement_id, advertisement)


@app.delete("/advertisement/{advertisement_id}")
def delete_advertisement(
    advertisement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_required),
):
    db_advertisement = crud.get_advertisement(db, advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if current_user.group != "admin" and db_advertisement.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.delete_advertisement(db, advertisement_id)
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
