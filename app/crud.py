from sqlalchemy.orm import Session
from app import models, schemas


def create_advertisement(db: Session, advertisement: schemas.AdvertisementCreate):
    db_advertisement = models.Advertisement(**advertisement.model_dump())
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
                           price: float = None, author: str = None):
    query = db.query(models.Advertisement)
    if title is not None:
        query = query.filter(models.Advertisement.title.ilike(f"%{title}%"))
    if description is not None:
        query = query.filter(models.Advertisement.description.ilike(f"%{description}%"))
    if price is not None:
        query = query.filter(models.Advertisement.price == price)
    if author is not None:
        query = query.filter(models.Advertisement.author.ilike(f"%{author}%"))
    return query.all()
