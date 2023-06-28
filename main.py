from fastapi import FastAPI, Response, status
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()


# class BASEMODEL_CLASS_TYPE(BaseModel):
#     key1: type
#     key2: type
#     key3: type

# @app.METHOD("/ENDPOINT/{PATH_PARAM}")
# def any_name(PATH_PARAM: TYPE, QUERY_PARAMS: TYPE, BODY: BASEMODEL_CLASS_TYPE):
#     # LOGIC
#     return {"data": "secret"}

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
        return {"success": True}
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"success": False}


@app.post("/create_account")
def create_acc(create_user: CreateAccount,response: Response):
    """get data, if present in database
    response.status_code = status.HTTP_403_FORBIDDEN
    return{"success": False}
    """
    response.status_code = status.HTTP_201_CREATED                                                          #for user creation
    return {"name": create_user.name, "email": create_user.email, "User Created": True}


