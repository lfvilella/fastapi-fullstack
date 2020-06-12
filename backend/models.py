import sqlalchemy
import sqlalchemy.orm
import uuid

from .database import Base


class Entity(Base):
    __tablename__ = "entities"

    cpf_cnpj = sqlalchemy.Column(
        sqlalchemy.String, primary_key=True, unique=True, index=True
    )
    name = sqlalchemy.Column(sqlalchemy.String)
    type_entity = sqlalchemy.Column(sqlalchemy.String(2))
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)


class Charge(Base):
    __tablename__ = "charges"

    id = sqlalchemy.Column(
        sqlalchemy.String,
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    # Field cpf_cnpj do devedor da class Entity
    debtor_cpf_cnpj = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.ForeignKey("entities.cpf_cnpj")
    )
    # Field cpf_cnpj do credor da class Entity
    creditor_cpf_cnpj = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.ForeignKey("entities.cpf_cnpj")
    )
    debito = sqlalchemy.Column(sqlalchemy.Float)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime)
    payed_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=None)


class APIKey(Base):
    __tablename__ = "apikeys"

    id = sqlalchemy.Column(
        sqlalchemy.String,
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    cpf_cnpj = sqlalchemy.Column(
        sqlalchemy.String,
        sqlalchemy.ForeignKey("entities.cpf_cnpj"),
        nullable=True,
        default=None,
    )
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime)
