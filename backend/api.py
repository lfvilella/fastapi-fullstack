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

    db_entity = data_access.create_entity(
        db=db, entity=schemas.Entity(**entity.dict()), persist=False
    )
    data_access.entity_set_password(
        db=db, cpf_cnpj=entity.cpf_cnpj, password=entity.password, persist=False
    )
    db.commit()
    return db_entity


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
    charge: schemas.ChargeCreate,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    try:
        return data_access.create_charge(db=db, charge=charge, api_key=api_key)
    except data_access.APIKeyNotFound:
        raise fastapi.HTTPException(status_code=403)
    except data_access.ValidationError as error:
        raise fastapi.HTTPException(status_code=400, detail=str(error))


@app.get(_VERSION + "/charge/{charge_id}", response_model=schemas.ChargeDatabase)
def read_charge(
    charge_id: str,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    try:
        return data_access.get_charge_by_id(db, charge_id=charge_id, api_key=api_key)
    except data_access.APIKeyNotFound:
        raise fastapi.HTTPException(status_code=403)
    except data_access.ValidationError as error:
        raise fastapi.HTTPException(status_code=404, detail=str(error))


@app.get(_VERSION + "/charge", response_model=typing.List[schemas.ChargeDatabase])
def filter_charge(
    debtor_cpf_cnpj: str = None,
    creditor_cpf_cnpj: str = None,
    is_active: bool = None,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    charge_filter = schemas.ChargeFilter(
        debtor_cpf_cnpj=debtor_cpf_cnpj,
        creditor_cpf_cnpj=creditor_cpf_cnpj,
        is_active=is_active,
    )
    try:
        return data_access.filter_charge(
            db, charge_filter=charge_filter, api_key=api_key
        )
    except data_access.APIKeyNotFound:
        raise fastapi.HTTPException(status_code=403)
    except data_access.ValidationError as error:
        raise fastapi.HTTPException(status_code=404, detail=str(error))


@app.post(_VERSION + "/charge/payment", response_model=schemas.ChargeDatabase)
def charge_payment(
    payment_info: schemas.ChargePayment,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):

    try:
        return data_access.payment_charge(
            db, payment_info=payment_info, api_key=api_key
        )
    except data_access.APIKeyNotFound:
        raise fastapi.HTTPException(status_code=403)
    except data_access.ValidationError as error:
        raise fastapi.HTTPException(status_code=400, detail=str(error))


@app.post(_VERSION + "/authenticate", response_model=schemas.APIKey)
def authenticate_login(
    login: schemas.Authenticate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    entity = data_access.get_entity_by_cpf_cnpj_and_password(
        db, cpf_cnpj=login.cpf_cnpj, password=login.password
    )
    if not entity:
        raise fastapi.HTTPException(status_code=400, detail="Invalid Credencials")

    api_key = data_access.create_entity_api_key(db, cpf_cnpj=entity.cpf_cnpj)
    return schemas.APIKey(api_key=api_key.id, cpf_cnpj=entity.cpf_cnpj)
