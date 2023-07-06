from typing import List

import uvicorn
from fastapi import FastAPI, Response, status, Depends
from sqlalchemy.orm import Session

import crud
import models
from db_connector import engine, Base, get_db
from email_service_client import send_email
from log_config import logger
from schemas import LoginSchema, CreateAccount, CreateBlog, UpdateBlog

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.post("/api/users/login")
def user_login(login_schema: LoginSchema, response: Response):
    if login_schema.email == "admin@test.com" and login_schema.password == "admin":
        logger.info("Successful login")
        return {"success": True}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    logger.warning("Unauthorized user")
    return {"success": False}


@app.post("/api/users/register")
def user_register(create_user: CreateAccount, response: Response, db: Session = Depends(get_db)):
    """TODO: get data, if present in database
    response.status_code = status.HTTP_403_FORBIDDEN
    return{"success": False}
    """
    crud.create_user(db, create_user.email, create_user.password, create_user.name)
    response.status_code = status.HTTP_201_CREATED  # for user creation
    return {"name": create_user.name, "email": create_user.email, "User Created": True}


@app.get("/api/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_record: models.User = crud.get_user(db, user_id)
    return user_record


@app.post("/api/blogs")
def create_blog(create_blog_payload: CreateBlog, response: Response, db: Session = Depends(get_db)):
    crud.create_blog(db, create_blog_payload.topic, create_blog_payload.data)
    response.status_code = status.HTTP_201_CREATED
    email_response = send_email()
    logger.debug(f"Email Response: {email_response}")
    response = {
        "topic": create_blog_payload.topic,
        "content": create_blog_payload.data,
        "email_sent": False
    }
    if email_response.get("success"):
        response["email_sent"] = True
    return response


@app.get("/api/blogs/{blog_id}")
def read_blog(blog_id: int, db: Session = Depends(get_db)):
    blog_record: models.Blog = crud.read_blog(db, blog_id)
    return blog_record


@app.get("/api/blogs")
def read_all_blog(db: Session = Depends(get_db)):
    blog_records: List[models.Blog] = crud.read_all_blog(db)
    return blog_records


@app.put("/api/blogs/{blog_id}")
def update_blog(blog_id, update_blog_payload: UpdateBlog, db: Session = Depends(get_db)):
    updated_record = crud.update_blog(db, blog_id, update_blog_payload.topic, update_blog_payload.data)
    return updated_record


@app.delete("/api/blogs/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    crud.delete_blog(db, blog_id)
    response = {"success": True}
    return response


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
