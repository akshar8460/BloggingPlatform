from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/sum")
def add(a: int, b: int):
    return {"sum": a+b}


@app.get("/diff")
def add(a: int, b: int):
    return {"diff": a-b}