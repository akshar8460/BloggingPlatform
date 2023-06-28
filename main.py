import logging

from fastapi import FastAPI, Response, status, Depends
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

import crud
from db_connector import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# class BASEMODEL_CLASS_TYPE(BaseModel):
#     key1: type
#     key2: type
#     key3: type

# @app.METHOD("/ENDPOINT/{PATH_PARAM}")
# def any_name(PATH_PARAM: TYPE, QUERY_PARAMS: TYPE, BODY: BASEMODEL_CLASS_TYPE):
#     # LOGIC
#     return {"data": "secret"}

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler and set the log level
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

# Create a console handler and set the log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=5, max_length=20)


class CreateAccount(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=5, max_length=20)


@app.post("/login")
def login(login_schema: LoginSchema, response: Response):
    if login_schema.email == "admin@test.com" and login_schema.password == "admin":
        logger.info("Successful login")
        return {"success": True}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    logger.warning("Unauthorized user")
    return {"success": False}


@app.post("/create_account")
def create_acc(create_user: CreateAccount, response: Response, db: Session = Depends(get_db)):
    """get data, if present in database
    response.status_code = status.HTTP_403_FORBIDDEN
    return{"success": False}
    """
    db_user = crud.create_user(db, create_user.email, create_user.password, create_user.name)
    response.status_code = status.HTTP_201_CREATED  # for user creation
    return {"name": create_user.name, "email": create_user.email, "User Created": True}
