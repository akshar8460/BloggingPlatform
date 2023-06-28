from fastapi import FastAPI, Response, status, Depends
from sqlalchemy.orm import Session

import crud
from db_connector import engine, Base, get_db
from log_config import logger
from schemas import LoginSchema, CreateAccount, CreateBlog

Base.metadata.create_all(bind=engine)
app = FastAPI()


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
    crud.create_user(db, create_user.email, create_user.password, create_user.name)
    response.status_code = status.HTTP_201_CREATED  # for user creation
    return {"name": create_user.name, "email": create_user.email, "User Created": True}
