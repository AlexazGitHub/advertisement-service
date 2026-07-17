from datetime import datetime
from sqlalchemy.orm import Session
from app import models, schemas, auth


# ---------- Advertisement ----------

def create_advertisement(db: Session, advertisement: schemas.AdvertisementCreate, owner_id: int = None):
    db_advertisement = models.Advertisement(**advertisement.model_dump(), owner_id=owner_id)
    db.add(db_advertisement)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement


def get_advertisement(db: Session, advertisement_id: int):
    return db.query(models.Advertisement).filter(
        models.Advertisement.id == advertisement_id
    ).first()


def update_advertisement(db: Session, advertisement_id: int, advertisement: schemas.AdvertisementUpdate):
    db_advertisement = get_advertisement(db, advertisement_id)
    if db_advertisement is None:
        return None
    update_data = advertisement.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_advertisement, key, value)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement


def delete_advertisement(db: Session, advertisement_id: int):
    db_advertisement = get_advertisement(db, advertisement_id)
    if db_advertisement is None:
        return None
    db.delete(db_advertisement)
    db.commit()
    return db_advertisement


def search_advertisements(db: Session, title: str = None, description: str = None,
                           price: float = None, author: str = None,
                           created_at_from: datetime = None, created_at_to: datetime = None):
    query = db.query(models.Advertisement)
    if title is not None:
        query = query.filter(models.Advertisement.title.ilike(f"%{title}%"))
    if description is not None:
        query = query.filter(models.Advertisement.description.ilike(f"%{description}%"))
    if price is not None:
        query = query.filter(models.Advertisement.price == price)
    if author is not None:
        query = query.filter(models.Advertisement.author.ilike(f"%{author}%"))
    if created_at_from is not None:
        query = query.filter(models.Advertisement.created_at >= created_at_from)
    if created_at_to is not None:
        query = query.filter(models.Advertisement.created_at <= created_at_to)
    return query.all()


# ---------- User ----------

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        hashed_password=auth.hash_password(user.password),
        group=user.group,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user is None:
        return None
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = auth.hash_password(update_data.pop("password"))
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user is None:
        return None
    db.delete(db_user)
    db.commit()
    return db_user
