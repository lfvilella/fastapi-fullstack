import fastapi
import sqlalchemy.orm
import typing
from . import schemas, data_access, database, models

# Create DB
models.Base.metadata.create_all(bind=database.engine)

app = fastapi.FastAPI()
_VERSION = "/v.1"


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(_VERSION + "/entity", response_model=schemas.Entity)
def create_entity(
    entity: schemas.EntityCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    db_entity = data_access.get_entity_by_cpf_cnpj(db, cpf_cnpj=entity.cpf_cnpj)
    if db_entity:
        raise fastapi.HTTPException(status_code=400, detail="Entity alredy exist")

    return data_access.create_entity(db=db, entity=entity)


@app.get(_VERSION + "/entity/{cpf_cnpj}", response_model=schemas.Entity)
def read_entity(cpf_cnpj: str, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    db_entity = data_access.get_entity_by_cpf_cnpj(db, cpf_cnpj=cpf_cnpj)
    if not db_entity:
        raise fastapi.HTTPException(status_code=404, detail="Entity does not exist")

    return db_entity


@app.get(_VERSION + "/entity", response_model=typing.List[schemas.Entity])
def filter_entity(
    type_entity: schemas.EntityTypeEnum = None,
    limit: int = 100,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
) -> schemas.Entity:
    entities = data_access.filter_entity(db, type_entity, limit)
    if not entities:
        raise fastapi.HTTPException(status_code=404, detail="Entities not found")

    return entities
