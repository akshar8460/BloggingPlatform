from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import OperationalError

from db_connector import Base, engine
from log_config import logger

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database connection established successfully")
except OperationalError:
    logger.error("Failed to establish connection to the database.")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)


class Blog(Base):
    __tablename__ = "blog"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic = Column(String, unique=True, index=True)
    data = Column(String)
