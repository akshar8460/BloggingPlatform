from __future__ import annotations

from typing import List

import uvicorn
from fastapi import FastAPI, Response, status, Depends
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

import crud
import models
from db_connector import Base, engine
from db_connector import get_db
from email_service_client import send_email
from log_config import logger
from schemas import LoginSchema, CreateAccount, CreateBlog, UpdateBlog, UpdateUser
from utils import create_access_token, verify_access_token

app = FastAPI()


@app.post("/api/users/login")
def user_login(login_schema: LoginSchema, response: Response, db: Session = Depends(get_db)):
    """
        Endpoint for user login.
        Args:
            login_schema (LoginSchema): The login credentials provided by the user.
            response (Response): The HTTP response object.
            db (Session, optional): The database session. Defaults to Depends(get_db).
        Returns:
            dict: The login response containing a success flag and a token if login is successful,
            otherwise returns an error response with a 401 status code.
        """

    record = crud.get_user_email(db, login_schema.email)
    if record is not None and login_schema.password == record.password:
        # Login Success
        logger.info("Successful login")
        token = create_access_token({"sub": str(record.id)})
        return {"success": True, "token": token}
    # Login Failure
    response.status_code = status.HTTP_401_UNAUTHORIZED
    logger.warning("Unauthorized user" + login_schema.email)
    return {"success": False, "token": None}


@app.post("/api/users/register")
def user_register(create_user: CreateAccount, response: Response, db: Session = Depends(get_db)):
    """
        Endpoint for user registration.
        Args:
            create_user (CreateAccount): The user account details to create.
            response (Response): The HTTP response object.
            db (Session, optional): The database session. Defaults to Depends(get_db).
        Returns:
            dict: The registration response containing the user's name, email, and a success flag,
            or returns an error response with a 403 status code if the user already exists.
        """
    record = crud.get_user_email(db, create_user.email)
    if record is not None:
        response.status_code = status.HTTP_403_FORBIDDEN
        logger.warning("User exists")
        return {"success": False}
    user_record: models.User = crud.create_user(db, create_user.email, create_user.password, create_user.name)
    response.status_code = status.HTTP_201_CREATED  # for user creation
    logger.debug("New User Registered")
    data = {
        "template_data": {"name": create_user.name,
                          "country": "Delhi"
                          },
        "email": create_user.email,
        "type": "register_user"
    }
    # Send email message in RabbitMQ for Email Microservice
    send_email(payload=data)
    return {"name": user_record.name, "email": user_record.email, "id":user_record.id , "success": True}


@app.get("/api/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), token_verification=Depends(verify_access_token)):
    """
        Endpoint to retrieve user data by user ID.
        Args:
            user_id (int): The ID of the user to retrieve.
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            models.User: The user data for the specified user ID.
        """
    user_record: models.User = crud.get_user(db, user_id)
    logger.debug("User data fetched" + str(user_id))
    return user_record


@app.get("/api/users/")
def get_all_users(db: Session = Depends(get_db), token_verification=Depends(verify_access_token)):
    """
        Endpoint to retrieve all user records.
        Args:
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            List[models.User]: A list of all user records.
        """
    users_records: List[models.User] = crud.get_all_users(db)
    logger.debug("All user records fetched")
    return users_records


@app.put("/api/users/{user_id}")
def update_user(user_id, update_user_payload: UpdateUser, db: Session = Depends(get_db),
                token_verification=Depends(verify_access_token)):
    """
        Endpoint to update user data by user ID.
        Args:
            user_id (int): The ID of the user to update.
            update_user_payload (UpdateUser): The payload containing the updated user data.
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            models.User: The updated user data.
        """
    updated_user = crud.update_user(db, user_id, email=update_user_payload.email, name=update_user_payload.name,
                                    password=update_user_payload.password)
    logger.info("user date updated: " + str(user_id))
    return updated_user


@app.delete("/api/users/{user_id}")
def delete_user(user_id, db: Session = Depends(get_db), token_verification=Depends(verify_access_token)):
    """
        Endpoint to delete a user by user ID.
        Args:
            user_id (int): The ID of the user to delete.
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            dict: A response indicating the success of the deletion.

        """
    crud.delete_user(db, user_id)
    response = {"success": True}
    logger.debug("User Deleted " + str(user_id))
    return response


@app.post("/api/blogs")
def create_blog(create_blog_payload: CreateBlog, response: Response, db: Session = Depends(get_db),
                token_verification=Depends(verify_access_token)):
    """
        Endpoint to create a new blog.
        Args:
            create_blog_payload (CreateBlog): The payload containing the blog details.
            response (Response): The HTTP response object.
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            dict: The response containing the created blog details.
        """
    crud.create_blog(db, create_blog_payload.topic, create_blog_payload.data)
    response.status_code = status.HTTP_201_CREATED
    response = {
        "topic": create_blog_payload.topic,
        "content": create_blog_payload.data
    }
    return response


@app.get("/api/blogs/{blog_id}")
def read_blog(blog_id: int, db: Session = Depends(get_db), token_verification=Depends(verify_access_token)):
    """
        Endpoint to read a blog by blog ID.
        Args:
            blog_id (int): The ID of the blog to read.
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            dict: The response containing the retrieved blog details.
        """
    blog_record: models.Blog = crud.read_blog(db, blog_id)
    logger.debug("Read Blog" + str(blog_id))
    return blog_record


@app.get("/api/blogs")
def read_all_blogs(db: Session = Depends(get_db), token_verification=Depends(verify_access_token)):
    """
        Endpoint to read all blogs.
        Args:
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            List[models.Blog]: A list of all blog records.
        """
    blog_records: List[models.Blog] = crud.read_all_blog(db)
    logger.debug("Read all blogs")
    return blog_records


@app.put("/api/blogs/{blog_id}")
def update_blog(blog_id, update_blog_payload: UpdateBlog, db: Session = Depends(get_db),
                token_verification=Depends(verify_access_token)):
    """
        Endpoint to update a blog by blog ID.
        Args:
            blog_id (int): The ID of the blog to update.
            update_blog_payload (UpdateBlog): The payload containing the updated blog data.
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            dict: The updated blog data.
        """
    updated_record = crud.update_blog(db, blog_id, update_blog_payload.topic, update_blog_payload.data)
    logger.debug("Blog updated" + str(blog_id))
    return updated_record


@app.delete("/api/blogs/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db), token_verification=Depends(verify_access_token)):
    """
        Endpoint to delete a blog by blog ID.
        Args:
            blog_id (int): The ID of the blog to delete.
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token_verification (bool, optional): The result of token verification. Defaults to Depends(verify_access_token).
        Returns:
            dict: A response indicating the success of the deletion.
        """
    crud.delete_blog(db, blog_id)
    response = {"success": True}
    logger.log("Blog deleted" + str(blog_id))
    return response


def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database connection established successfully")
    except OperationalError:
        logger.error("Failed to establish connection to the database.")


if __name__ == "__main__":
    create_tables()
    uvicorn.run(app, port=8000)
