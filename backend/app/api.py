import fastapi
import sqlalchemy.orm
import typing
from . import schemas, data_access, database, models


# Create DB
models.Base.metadata.create_all(bind=database.engine)

_VERSION = "/api/v.1"
_SESSION_KEY = "api_key"


app = fastapi.FastAPI(
    openapi_url=_VERSION + "/openapi.json",
    docs_url=_VERSION + "/docs",
)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_api_key_from_request(request: fastapi.Request):
    return request.query_params.get(_SESSION_KEY) or request.cookies.get(
        _SESSION_KEY
    )


@app.exception_handler(data_access.DataAccessException)
def handle_data_access_error(
    request: fastapi.Request, exception: data_access.DataAccessException
):
    if isinstance(exception, data_access.APIKeyNotFound):
        return fastapi.responses.JSONResponse(status_code=403)

    if isinstance(exception, data_access.ValidationError):
        return fastapi.responses.JSONResponse(
            status_code=400, content={"detail": str(exception)}
        )

    if isinstance(exception, data_access.DoesNotExisit):
        return fastapi.responses.JSONResponse(
            status_code=404, content={"detail": str(exception)}
        )

    raise exception


@app.post(_VERSION + "/entity", status_code=201, response_model=schemas.Entity)
def create_entity(
    entity: schemas.EntityCreate,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    return data_access.create_entity(
        db, entity=schemas.Entity(**entity.dict()), password=entity.password,
    )


@app.get(_VERSION + "/entity/{cpf_cnpj}", response_model=schemas.Entity)
def read_entity(
    cpf_cnpj: schemas.CpfOrCnpj,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    return data_access.get_entity_by_cpf_cnpj(
        db, cpf_cnpj=cpf_cnpj, api_key=api_key, raise_error=True
    )


@app.get(_VERSION + "/entity-logged", response_model=schemas.Entity)
def read_entity_logged(
    request: fastapi.Request,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    return data_access.get_entity_by_api_key(
        db, get_api_key_from_request(request)
    )


@app.get(_VERSION + "/entity", response_model=typing.List[schemas.Entity])
def filter_entity(
    type_entity: schemas.EntityTypeEnum = None,
    limit: int = 100,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    return data_access.filter_entity_by_type(
        db=db, type_entity=type_entity, limit=limit, api_key=api_key
    )


@app.post(
    _VERSION + "/charge",
    status_code=201,
    response_model=schemas.ChargeDatabase,
)
def create_charge(
    request: fastapi.Request,
    charge: schemas.ChargeCreate,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    return data_access.create_charge(
        db=db, charge=charge, api_key=get_api_key_from_request(request)
    )


@app.get(
    _VERSION + "/charge/{charge_id}", response_model=schemas.ChargeDatabase
)
def read_charge(
    charge_id: str,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    return data_access.get_charge_by_id(
        db, charge_id=charge_id, api_key=api_key
    )


@app.get(
    _VERSION + "/charge", response_model=typing.List[schemas.ChargeFullInfo]
)
def filter_charge(
    request: fastapi.Request,
    debtor_cpf_cnpj: schemas.CpfOrCnpj = None,
    creditor_cpf_cnpj: schemas.CpfOrCnpj = None,
    is_active: bool = None,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    charge_filter = schemas.ChargeFilter(
        debtor_cpf_cnpj=debtor_cpf_cnpj,
        creditor_cpf_cnpj=creditor_cpf_cnpj,
        is_active=is_active,
    )

    return data_access.filter_charge(
        db,
        charge_filter=charge_filter,
        api_key=get_api_key_from_request(request),
    )


@app.post(_VERSION + "/charge/payment", response_model=schemas.ChargeDatabase)
def charge_payment(
    request: fastapi.Request,
    payment_info: schemas.ChargePayment,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    return data_access.payment_charge(
        db,
        payment_info=payment_info,
        api_key=get_api_key_from_request(request),
    )


@app.post(_VERSION + "/authenticate", response_model=schemas.APIKey)
def authenticate_login(
    response: fastapi.Response,
    login: schemas.Authenticate,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    entity = data_access.get_entity_by_cpf_cnpj_and_password(
        db, cpf_cnpj=login.cpf_cnpj, password=login.password
    )

    api_key = data_access.create_api_key(db, cpf_cnpj=entity.cpf_cnpj)
    if login.set_cookie:
        response.set_cookie(key=_SESSION_KEY, value=api_key)

    return schemas.APIKey(api_key=api_key, cpf_cnpj=entity.cpf_cnpj)


@app.delete(_VERSION + "/authenticate", status_code=204)
def authenticate_logout(
    request: fastapi.Request,
    api_key: str = None,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db),
):
    data_access.delete_api_key(db, api_key=get_api_key_from_request(request))
    return {}
