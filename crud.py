from sqlalchemy.orm import Session

from models import *


def create_user(db: Session, email, password, name):
    db_user = User(email=email, password=password, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_blog(db: Session, topic, data):
    db_blog = Blog(topic=topic, data=data)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog


def delete_blog(db: Session, id):
    db_blog = db.query(Blog).filter(Blog.id == id).first()
    db.delete(db_blog)
    db.commit()
    return True
