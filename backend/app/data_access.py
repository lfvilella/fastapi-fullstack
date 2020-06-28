""" Data Access

This module is reponsible to handle all interactions to the database
"""

import sqlalchemy.orm
import typing
import datetime
import secrets
import hashlib
from . import models, schemas, security


class DataAccessException(Exception):
    """ Data Access Exception

    This error is raised when data passed to the function is not valid
    """
    pass


class APIKeyNotFound(DataAccessException):
    """ API Key Not Found

    This error is raised when the API Key string is not found in the database or is not valid
    """
    pass


class ValidationError(DataAccessException):
    pass


class DoesNotExisit(DataAccessException):
    pass


# ENTITY THINGS


def get_entity_by_cpf_cnpj(
    db: sqlalchemy.orm.Session,
    cpf_cnpj: str,
    api_key: str = None,
    validate_api_key=True,
    raise_error=False,
) -> models.Entity:
    if validate_api_key or api_key:
        check_api_key(db, api_key=api_key)

    db_entity = db.query(models.Entity).get(cpf_cnpj)
    if not db_entity:
        if raise_error:
            raise DoesNotExisit("Entity does not exist")

        return None

    return db_entity


def get_entity_by_api_key(
    db: sqlalchemy.orm.Session, api_key: str
) -> models.Entity:
    db_api_key = check_api_key(db, api_key=api_key)
    return get_entity_by_cpf_cnpj(
        db, db_api_key.cpf_cnpj, validate_api_key=False, raise_error=True
    )


def get_entity_by_cpf_cnpj_and_password(
    db: sqlalchemy.orm.Session, cpf_cnpj: str, password: str
) -> models.Entity:
    entity = get_entity_by_cpf_cnpj(db, cpf_cnpj, validate_api_key=False)
    if not entity:
        raise ValidationError("Invalid Credentials")

    if not security.verify_password(password, entity.hashed_password):
        raise ValidationError("Invalid Credentials")

    return entity


def create_entity(
    db: sqlalchemy.orm.Session,
    entity: schemas.Entity,
    password: bool = None,
    persist: bool = True,
) -> models.Entity:

    db_entity = get_entity_by_cpf_cnpj(
        db, cpf_cnpj=entity.cpf_cnpj, validate_api_key=False,
    )
    if db_entity and db_entity.hashed_password:
        raise ValidationError("Entity already exist")

    db_entity = db_entity or models.Entity()
    db_entity.cpf_cnpj = entity.cpf_cnpj
    db_entity.name = entity.name

    if password:
        entity_set_password(
            db=db,
            cpf_cnpj=entity.cpf_cnpj,
            password=password,
            entity=db_entity,
            persist=False,
        )

    db.add(db_entity)
    if persist:
        db.commit()

    db.flush()
    return db_entity


def get_entity_api_key_by_id(
    db: sqlalchemy.orm.Session, api_key: str
) -> models.APIKey:
    if not api_key:
        return None

    return db.query(models.APIKey).get(api_key)


def filter_entity_by_type(
    db: sqlalchemy.orm.Session,
    type_entity: str,
    api_key: str,
    limit: int = 100,
) -> typing.List[models.Entity]:
    check_api_key(db, api_key=api_key)

    query = (
        db.query(models.Entity).filter_by(type_entity=type_entity).limit(limit)
    )

    if not query.all():
        raise DoesNotExisit("Entities not found")

    return query.all()


def entity_set_password(
    db: sqlalchemy.orm.Session,
    cpf_cnpj: str,
    password: str,
    entity: models.Entity = None,
    persist=True,
) -> models.Entity:
    entity = entity or get_entity_by_cpf_cnpj(
        db, cpf_cnpj, validate_api_key=False
    )

    if not entity:
        raise DoesNotExisit("Entity does not exist")

    entity.hashed_password = security.get_password_hash(password)
    db.add(entity)
    db.flush()
    if persist:
        db.commit()
    return entity


# APIKEY THINGS


def generate_api_key(identifier, verifier) -> str:
    return f"{identifier}.{verifier}"


def split_api_key(api_key: str) -> typing.Tuple[str]:
    try:
        identifier, verifier = str(api_key).split(".")
        return (identifier, verifier)
    except ValueError:
        raise APIKeyNotFound()


def create_api_key(
    db: sqlalchemy.orm.Session, cpf_cnpj: str, persist=True
) -> str:
    verifier = secrets.token_hex(16)
    db_api_key = models.APIKey(
        cpf_cnpj=cpf_cnpj,
        created_at=datetime.datetime.utcnow(),
        verifier_hash=hashlib.sha256(verifier.encode("utf-8")).hexdigest(),
    )
    db.add(db_api_key)
    db.flush()
    if persist:
        db.commit()
    return generate_api_key(db_api_key.id, verifier)


def delete_api_key(db: sqlalchemy.orm.Session, api_key: str) -> models.APIKey:
    db_api_key = check_api_key(db, api_key=api_key)

    filter_api_key = (
        db.query(models.APIKey).filter_by(cpf_cnpj=db_api_key.cpf_cnpj).all()
    )

    for item in filter_api_key:
        db.delete(item)

    db.commit()
    return db_api_key


def check_api_key(db: sqlalchemy.orm.Session, api_key: str) -> models.APIKey:
    """ Check API Key
    This method is used to verify API Key is valid

    Args:
        api_key (str): identifier.verifier e.g RaNdomString.Verifier

    Raises:
        APIKeyNotFound: The raises is not valid or not found error when API Key not exist.
    """
    indentifier, verifier = split_api_key(api_key)

    db_api_key = get_entity_api_key_by_id(db, api_key=indentifier)
    if not db_api_key:
        raise APIKeyNotFound()

    verifier_hash = hashlib.sha256(verifier.encode("utf-8")).hexdigest()
    if verifier_hash != db_api_key.verifier_hash:
        raise APIKeyNotFound()

    return db_api_key


# CHARGE THINGS


def get_charge_by_id(
    db: sqlalchemy.orm.Session, charge_id: str, api_key: str
) -> models.Charge:
    check_api_key(db, api_key=api_key)
    db_charge = db.query(models.Charge).get(charge_id)

    if not db_charge:
        raise DoesNotExisit("Charge does not exist")

    return db_charge


def get_charge_by_creditor_cpf_cnpj(
    db: sqlalchemy.orm.Session, creditor_cpf_cnpj: str
) -> models.Charge:
    return db.query(models.Charge).get(creditor_cpf_cnpj)


def filter_charge(
    db: sqlalchemy.orm.Session,
    charge_filter: schemas.ChargeFilter,
    api_key: str,
) -> typing.List[schemas.ChargeFullInfo]:
    check_api_key(db, api_key=api_key)

    Debitor = sqlalchemy.orm.aliased(models.Entity)
    Creditor = sqlalchemy.orm.aliased(models.Entity)
    query = (
        db.query(models.Charge, Debitor, Creditor,)
        .join(Debitor, Debitor.cpf_cnpj == models.Charge.debtor_cpf_cnpj)
        .join(Creditor, Creditor.cpf_cnpj == models.Charge.creditor_cpf_cnpj)
    )

    if charge_filter.debtor_cpf_cnpj:
        query = query.filter(
            models.Charge.debtor_cpf_cnpj == charge_filter.debtor_cpf_cnpj
        )

    if charge_filter.creditor_cpf_cnpj:
        query = query.filter(
            models.Charge.creditor_cpf_cnpj == charge_filter.creditor_cpf_cnpj
        )

    if charge_filter.is_active is not None:
        query = query.filter(
            models.Charge.is_active == charge_filter.is_active
        )

    rows = query.all()
    if not rows:
        raise DoesNotExisit("Charge not found")

    full_charges_info = []
    for charge_db, debitor_db, creditor_db in rows:
        charge_info = schemas.ChargeFullInfo(
            id=charge_db.id,
            debtor=debitor_db,
            creditor=creditor_db,
            debito=charge_db.debito,
            is_active=charge_db.is_active,
            created_at=charge_db.created_at,
            payed_at=charge_db.payed_at,
        )
        full_charges_info.append(charge_info)

    return full_charges_info


def create_charge(
    db: sqlalchemy.orm.Session, charge: schemas.ChargeCreate, api_key: str
) -> models.Charge:

    db_api_key = check_api_key(db, api_key=api_key)

    debtor_db = get_entity_by_cpf_cnpj(
        db, charge.debtor.cpf_cnpj, validate_api_key=False
    )
    creditor_db = get_entity_by_cpf_cnpj(
        db, charge.creditor_cpf_cnpj, validate_api_key=False
    )

    if creditor_db.cpf_cnpj != db_api_key.cpf_cnpj:
        raise ValidationError("CPF / CNPJ is not the same as the creditor")

    if not debtor_db:
        debtor_db = create_entity(db, charge.debtor, persist=False)

    db_charge = models.Charge(
        debtor_cpf_cnpj=debtor_db.cpf_cnpj,
        creditor_cpf_cnpj=creditor_db.cpf_cnpj,
        debito=charge.debito,
        is_active=True,
    )
    db.add(db_charge)
    db.commit()
    return db_charge


def payment_charge(
    db: sqlalchemy.orm.Session,
    payment_info: schemas.ChargePayment,
    api_key: str,
) -> models.Charge:
    db_api_key = check_api_key(db, api_key=api_key)

    db_charge = get_charge_by_id(
        db, charge_id=payment_info.id, api_key=api_key
    )

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
