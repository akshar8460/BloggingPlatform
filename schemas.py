from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=5, max_length=20)


class CreateAccount(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=5, max_length=20)


class UpdateUser(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=5, max_length=20)


class CreateBlog(BaseModel):
    topic: str = Field(max_length=25)
    data: str


class UpdateBlog(BaseModel):
    topic: str = Field(max_length=25)
    data: str
