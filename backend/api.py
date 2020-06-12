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
):
    entities = data_access.filter_entity_by_type(db, type_entity, limit)
    if not entities:
        raise fastapi.HTTPException(status_code=404, detail="Entities not found")

    return entities


@app.post(_VERSION + "/charge", response_model=schemas.ChargeDatabase)
def create_charge(
    charge: schemas.ChargeCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    return data_access.create_charge(db=db, charge=charge)


@app.get(_VERSION + "/charge/{charge_id}", response_model=schemas.ChargeDatabase)
def read_charge(charge_id: str, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    db_charge = data_access.get_charge_by_id(db, charge_id=charge_id)
    if not db_charge:
        raise fastapi.HTTPException(status_code=404, detail="Charge does not exist")

    return db_charge


@app.get(_VERSION + "/charge", response_model=typing.List[schemas.ChargeDatabase])
def filter_charge(
    debtor_cpf_cnpj: str = None,
    creditor_cpf_cnpj: str = None,
    is_active: bool = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    charge_filter = schemas.ChargeFilter(
        debtor_cpf_cnpj=debtor_cpf_cnpj,
        creditor_cpf_cnpj=creditor_cpf_cnpj,
        is_active=is_active,
    )
    charges = data_access.filter_charge(db, charge_filter=charge_filter)
    if not charges:
        raise fastapi.HTTPException(status_code=404, detail="Charge not found")

    return charges


@app.post(_VERSION + "/charge/payment", response_model=schemas.ChargeDatabase)
def charge_payment(
    payment_info: schemas.ChargePayment,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    
    try:
        return data_access.payment_charge(db, payment_info)
    except ValueError as error:
        raise fastapi.HTTPException(status_code=400, detail=str(error))
