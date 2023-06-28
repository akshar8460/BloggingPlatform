from fastapi import FastAPI, Response, status
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
def login(login_schema: LoginSchema, response: Response):
    if login_schema.email == "admin@test.com" and login_schema.password == "admin":
        return {"success": True}
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"success": False}



