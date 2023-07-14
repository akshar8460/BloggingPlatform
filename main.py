from datetime import timedelta, datetime
from typing import List, Annotated

import uvicorn
from fastapi import FastAPI, Response, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import crud
import models
from db_connector import engine, Base, get_db
from email_service_client import send_email
from log_config import logger
from schemas import LoginSchema, CreateAccount, CreateBlog, UpdateBlog, UpdateUser

Base.metadata.create_all(bind=engine)
app = FastAPI()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Todo: Change according to your needs.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError as exc:
        print(exc)
        raise credentials_exception
    return True


@app.post("/api/users/login")
def user_login(login_schema: LoginSchema, response: Response, db: Session = Depends(get_db)):
    record = crud.get_user_email(db, login_schema.email)
    if record is not None and login_schema.password == record.password:
        # Login Success
        logger.info("Successful login")
        token = create_access_token({"sub": str(record.id)})
        return {"success": True, "token": token}
    # Login failed
    response.status_code = status.HTTP_401_UNAUTHORIZED
    logger.warning("Unauthorized user" + login_schema.email)
    return {"success": False, "token": None}


@app.get("/api/secure_api")
def secure_api(token_verification=Depends(verify_access_token)):
    return {"data": "secret data"}


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


@app.get("/api/users/")
def get_all_users(db: Session = Depends(get_db)):
    users_records: List[models.User] = crud.get_all_users(db)
    return users_records


@app.put("/api/users/{user_id}")
def update_blog(user_id, update_user_payload: UpdateUser, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, update_user_payload.email, update_user_payload.name,
                                    update_user_payload.password)
    return updated_user


@app.delete("/api/users/{user_id}")
def delete_user(user_id, db: Session = Depends(get_db)):
    crud.delete_user(db, user_id)
    response = {"success": True}
    return response


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
