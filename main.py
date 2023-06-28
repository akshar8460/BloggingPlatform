from fastapi import FastAPI
from pydantic import BaseModel

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
    email: str
    password: str


@app.post("/login")
def login(login_schema: LoginSchema):
    if login_schema.email == "admin@test.com" and login_schema.password == "admin":
        return {"success": True}
    return {"success": False}, 404
