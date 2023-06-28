from sqlalchemy.orm import Session

import models


def create_user(db: Session, email, password, name):
    db_user = models.User(email=email, password=password, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_blog(db:Session,topic,data):
    db_blog = models.Blog(topic=topic, data=data)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog