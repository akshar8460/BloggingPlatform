from sqlalchemy import Column, Integer, String

from db_connector import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)
