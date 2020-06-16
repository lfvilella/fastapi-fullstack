import pydantic
import enum
import validate_docbr
import typing
import datetime


class CpfOrCnpj(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")

        cpf, cnpj = validate_docbr.CPF(), validate_docbr.CNPJ()
        if not (cpf.validate(v) or cnpj.validate(v)):
            raise TypeError("Invalid CPF / CNPJ")

        return "".join(filter(str.isdigit, v))

    def __repr__(self):
        return f"CpfOrCnpj({super().__repr__()})"


class EntityTypeEnum(str, enum.Enum):
    pj = "pj"
    pf = "pf"


class EntityBase(pydantic.BaseModel):
    class Config:
        orm_mode = True

    name: str
    cpf_cnpj: CpfOrCnpj


class Entity(EntityBase):
    type_entity: typing.Optional[EntityTypeEnum] = None

    @pydantic.validator("type_entity", pre=True, always=True)
    def validate_type_entity(cls, v, values):
        if "cpf_cnpj" not in values:
            return None

        cpf_cnpj = values["cpf_cnpj"]

        cpf, cnpj = validate_docbr.CPF(), validate_docbr.CNPJ()
        if cpf.validate(cpf_cnpj):
            return EntityTypeEnum.pf

        if cnpj.validate(cpf_cnpj):
            return EntityTypeEnum.pj

        return None


class EntityCreate(EntityBase):
    password: str


class ChargeCreate(pydantic.BaseModel):
    class Config:
        orm_mode = True

    debtor: EntityBase
    creditor_cpf_cnpj: CpfOrCnpj
    debito: pydantic.PositiveFloat

    @pydantic.validator("creditor_cpf_cnpj")
    def validate_creditor_cpf_cnpj(cls, v, values):
        if "debtor" not in values:
            raise ValueError("Debtor not found")

        debtor_cpf_cnpj = values["debtor"].cpf_cnpj
        creditor_cpf_cnpj = "".join(filter(str.isdigit, v))
        if debtor_cpf_cnpj == creditor_cpf_cnpj:
            raise ValueError("You can not add debt for yourself")

        return creditor_cpf_cnpj


class ChargeDatabase(pydantic.BaseModel):
    class Config:
        orm_mode = True

    id: str
    debtor_cpf_cnpj: CpfOrCnpj
    creditor_cpf_cnpj: CpfOrCnpj
    debito: pydantic.PositiveFloat
    is_active: bool
    created_at: datetime.datetime
    payed_at: datetime.datetime = None


class ChargeFilter(pydantic.BaseModel):
    debtor_cpf_cnpj: typing.Optional[CpfOrCnpj] = None
    creditor_cpf_cnpj: typing.Optional[CpfOrCnpj] = None
    is_active: typing.Optional[bool] = None


class ChargePayment(pydantic.BaseModel):
    id: str
    creditor_cpf_cnpj: CpfOrCnpj


class Authenticate(pydantic.BaseModel):
    cpf_cnpj: CpfOrCnpj
    password: str


class Logout(pydantic.BaseModel):
    cpf_cnpj: CpfOrCnpj


class APIKey(pydantic.BaseModel):
    api_key: str
    cpf_cnpj: CpfOrCnpj
