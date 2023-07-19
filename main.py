from __future__ import annotations

from datetime import timedelta, datetime
from typing import List, Annotated

import uvicorn
from fastapi import FastAPI, Response, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import crud
import models
from db_connector import get_db
from email_service_client import send_email
from log_config import logger
from schemas import LoginSchema, CreateAccount, CreateBlog, UpdateBlog, UpdateUser

app = FastAPI()
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Change as your needs
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
        Creates an access token using the given data and expiration time.
        Args:
            data (dict): The data to encode in the access token.
            expires_delta (timedelta | None, optional): The expiration time for the token.
                If None, a default expiration time of 15 minutes will be used.
                Defaults to None.
        Returns:
            str: The encoded access token.
        """
    to_encode = data.copy()
    if expires_delta:
        # Calculate expiration time if expires_delta is provided
        expire = datetime.utcnow() + expires_delta
    else:
        # Use default expiration time of 15 minutes
        expire = datetime.utcnow() + timedelta(minutes=15)

    # Add expiration time to the data to be encoded
    to_encode.update({"exp": expire})

    # Encode the data into a JWT using the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    """
        Verifies the provided access token.
        Args:
            token (str): The access token to verify.
        Returns:
            bool: True if the token is valid, otherwise raises an HTTPException.
        """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract the subject claim from the payload
        sub: str = payload.get("sub")

        # If subject is None, raise credentials_exception
        if sub is None:
            raise credentials_exception
    except JWTError as exc:
        logger.warning(f"Token verification failed with following exception: {exc}")
        raise credentials_exception
    return True


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
    crud.create_user(db, create_user.email, create_user.password, create_user.name)
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
    return {"name": create_user.name, "email": create_user.email, "success": True}


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
    updated_user = crud.update_user(db, user_id, update_user_payload.email, update_user_payload.name,
                                    update_user_payload.password)
    logger.log("user date updated: " + str(user_id))
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
def read_all_blog(db: Session = Depends(get_db), token_verification=Depends(verify_access_token)):
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


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
