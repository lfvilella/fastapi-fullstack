import sqlalchemy.orm
import typing
from . import models, schemas


def get_entity_by_cpf_cnpj(db: sqlalchemy.orm.Session, cpf_cnpj: str) -> models.Entity:
    return db.query(models.Entity).get(cpf_cnpj)


def create_entity(
    db: sqlalchemy.orm.Session, entity: schemas.EntityCreate) -> models.Entity:
    entity_data = entity.dict()
    password = entity_data.pop("password")

    db_entity = models.Entity(**entity_data)
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def filter_entity(
    db: sqlalchemy.orm.Session, type_entity: str, limit: int = 100) -> typing.List[models.Entity]:
    query = db.query(models.Entity).filter_by(type_entity=type_entity).limit(limit)
    return query.all()
