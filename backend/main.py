from fastapi import FastAPI
from . import schemas

app = FastAPI()
_VERSION = 'v.1'

@app.get(_VERSION+"/users/{user_id}")
def read_user(user_id: int, password: str = None):
    return {"user_id": user_id, "password": password}