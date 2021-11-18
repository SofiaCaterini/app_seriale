from sqlalchemy.orm import Session
from . import models, schemas


def get_devices(db: Session):
    return db.query(models.Device).all()


def get_device(db: Session, id: int):
    return db.query(models.Device).get(id)


def create_device(db: Session, item: schemas.DeviceCreate):
    db_item = models.Device(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_device(db: Session, id: int):
    if db.query(models.Device).get(id):
        db.query(models.Device).filter_by(id=id).delete()
        db.commit()
        return {"status": True, "message": f"Record {id} deleted"}
    else:
        return {"status": False, "message": "No such record"}