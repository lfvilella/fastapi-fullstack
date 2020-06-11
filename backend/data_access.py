import sqlalchemy.orm
import typing
from . import models, schemas


def get_entity_by_cpf_cnpj(db: sqlalchemy.orm.Session, cpf_cnpj: str) -> models.Entity:
    return db.query(models.Entity).get(cpf_cnpj)


def create_entity(db: sqlalchemy.orm.Session, entity: schemas.EntityCreate, persist:bool = True) -> models.Entity:
    entity_data = entity.dict()
    password = entity_data.pop("password")

    db_entity = models.Entity(**entity_data)
    db.add(db_entity)
    if persist:
        db.commit()

    db.refresh(db_entity)
    return db_entity


def filter_entity_by_type(db: sqlalchemy.orm.Session,
                  type_entity: str, limit: int = 100) -> typing.List[models.Entity]:
    query = db.query(models.Entity).filter_by(type_entity=type_entity).limit(limit)
    return query.all()


def create_charge(db: sqlalchemy.orm.Session, charge: schemas.ChargeCreate) -> models.Charge:
    debtor_db = get_entity_by_cpf_cnpj(db, charge.debtor.cpf_cnpj)
    creditor_db = get_entity_by_cpf_cnpj(db, charge.creditor_cpf_cnpj)

    if not debtor_db:
        debtor_db = create_entity(db, charge.debtor, persist=False)

    db_charge = models.Charge(debtor_cpf_cnpj = debtor_db.cpf_cnpj,
                              creditor_cpf_cnpj = creditor_db.cpf_cnpj,
                              debito = charge.debito,
                              is_active = True)
    db.add(db_charge)
    db.commit()
    db.refresh(db_charge)
    return db_charge