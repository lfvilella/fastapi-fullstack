import sqlalchemy.orm
import typing
import uuid
import datetime
from . import models, schemas, security


class DataAccessException(Exception):
    pass


class APIKeyNotFound(DataAccessException):
    pass


class ValidationError(DataAccessException):
    pass


class DoesNotExisit(DataAccessException):
    pass


# ENTITY THINGS


def get_entity_by_cpf_cnpj(
    db: sqlalchemy.orm.Session, cpf_cnpj: str, api_key: str = None, raise_error=False
) -> models.Entity:
    if api_key:
        check_api_key(db, api_key=api_key)

    db_entity = db.query(models.Entity).get(cpf_cnpj)
    if not db_entity:
        if raise_error:
            raise DoesNotExisit("Entity does not exist")
        return None

    return db_entity


def get_entity_by_cpf_cnpj_and_password(
    db: sqlalchemy.orm.Session, cpf_cnpj: str, password: str
) -> models.Entity:
    entity = get_entity_by_cpf_cnpj(db, cpf_cnpj)
    if not entity:
        return None

    if not security.verify_password(password, entity.hashed_password):
        return None

    return entity


def create_entity(
    db: sqlalchemy.orm.Session, entity: schemas.Entity, persist: bool = True
) -> models.Entity:

    db_entity = models.Entity(**entity.dict())
    db.add(db_entity)
    if persist:
        db.commit()

    db.flush()
    return db_entity


def get_entity_api_key_by_id(db: sqlalchemy.orm.Session, api_key: str) -> models.APIKey:
    if not api_key:
        return None

    return db.query(models.APIKey).get(api_key)


def filter_entity_by_type(
    db: sqlalchemy.orm.Session, type_entity: str, api_key: str, limit: int = 100
) -> typing.List[models.Entity]:
    db_api_key = check_api_key(db, api_key=api_key)

    query = db.query(models.Entity).filter_by(type_entity=type_entity).limit(limit)

    if not query.all():
        raise DoesNotExisit("Entities not found")

    return query.all()


def entity_set_password(
    db: sqlalchemy.orm.Session, cpf_cnpj: str, password: str, persist=True
) -> models.Entity:
    entity = get_entity_by_cpf_cnpj(db, cpf_cnpj)

    if not entity:
        raise DoesNotExisit("Entity does not exist")

    entity.hashed_password = security.get_password_hash(password)
    db.add(entity)
    if persist:
        db.commit()
    return entity


# APIKEY THINGS


def create_api_key(db: sqlalchemy.orm.Session, cpf_cnpj: str) -> models.APIKey:

    db_api_key = models.APIKey(
        cpf_cnpj=cpf_cnpj, created_at=datetime.datetime.utcnow(),
    )
    db.add(db_api_key)
    db.commit()
    return db_api_key


def check_api_key(db: sqlalchemy.orm.Session, api_key: str):
    db_api_key = get_entity_api_key_by_id(db, api_key=api_key)
    if not db_api_key:
        raise APIKeyNotFound()

    return db_api_key


# CHARGE THINGS


def get_charge_by_id(
    db: sqlalchemy.orm.Session, charge_id: str, api_key: str
) -> models.Charge:
    db_api_key = check_api_key(db, api_key=api_key)
    db_charge = db.query(models.Charge).get(charge_id)

    if not db_charge:
        raise DoesNotExisit("Charge does not exist")

    return db_charge


def get_charge_by_creditor_cpf_cnpj(
    db: sqlalchemy.orm.Session, creditor_cpf_cnpj: str
) -> models.Charge:
    return db.query(models.Charge).get(creditor_cpf_cnpj)


def filter_charge(
    db: sqlalchemy.orm.Session, charge_filter: schemas.ChargeFilter, api_key: str
) -> typing.List[models.Charge]:
    db_api_key = check_api_key(db, api_key=api_key)

    query = db.query(models.Charge)
    if charge_filter.debtor_cpf_cnpj:
        query = query.filter_by(debtor_cpf_cnpj=charge_filter.debtor_cpf_cnpj)

    if charge_filter.creditor_cpf_cnpj:
        query = query.filter_by(creditor_cpf_cnpj=charge_filter.creditor_cpf_cnpj)

    if charge_filter.is_active is not None:
        query = query.filter_by(is_active=charge_filter.is_active)

    queries = query.all()
    if not queries:
        raise DoesNotExisit("Charge not found")

    return queries


def create_charge(
    db: sqlalchemy.orm.Session, charge: schemas.ChargeCreate, api_key: str
) -> models.Charge:

    db_api_key = check_api_key(db, api_key=api_key)

    debtor_db = get_entity_by_cpf_cnpj(db, charge.debtor.cpf_cnpj)
    creditor_db = get_entity_by_cpf_cnpj(db, charge.creditor_cpf_cnpj)

    if creditor_db.cpf_cnpj != db_api_key.cpf_cnpj:
        raise ValidationError("CPF / CNPJ is not the same as the creditor")

    if not debtor_db:
        debtor_db = create_entity(db, charge.debtor, persist=False)

    db_charge = models.Charge(
        debtor_cpf_cnpj=debtor_db.cpf_cnpj,
        creditor_cpf_cnpj=creditor_db.cpf_cnpj,
        debito=charge.debito,
        is_active=True,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(db_charge)
    db.commit()
    return db_charge


def payment_charge(
    db: sqlalchemy.orm.Session, payment_info: schemas.ChargePayment, api_key: str
) -> models.Charge:

    db_api_key = check_api_key(db, api_key=api_key)

    db_charge = get_charge_by_id(db, charge_id=payment_info.id, api_key=api_key)

    if not db_charge:
        raise DoesNotExisit("Charge not found to pay")

    if db_charge.creditor_cpf_cnpj != db_api_key.cpf_cnpj:
        raise ValidationError("CPF/CNPJ is not the same on charge")

    if db_charge.creditor_cpf_cnpj != payment_info.creditor_cpf_cnpj:
        raise ValidationError("CPF / CNPJ is not the same as the creditor")

    db_charge.payed_at = datetime.datetime.utcnow()
    db_charge.is_active = False
    db.add(db_charge)
    db.commit()
    return db_charge
