from sqlalchemy.orm import Session

import models


def create_user(db: Session, email, password, name):
    db_user = models.User(email=email, password=password, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
