from sqlalchemy import Column, Integer, String

from db_connector import Base


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




