from fastapi import FastAPI
from . import schemas

app = FastAPI()
_VERSION = '/v.1'

@app.post(_VERSION+"/person", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate):
    return schemas.Person(**person.dict())