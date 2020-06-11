import pydantic
import enum
import validate_docbr


class EntityTypeEnum(str, enum.Enum):
    pj = "pj"
    pf = "pf"


class Entity(pydantic.BaseModel):
    class Config:
        orm_mode = True

    name: str
    type_entity: EntityTypeEnum
    cpf_cnpj: str

    @pydantic.validator("cpf_cnpj")
    def validate_cpf_cnpj(cls, v, values):
        if "type_entity" not in values:
            raise ValueError("Entity Type is not defined")

        cpf, cnpj = validate_docbr.CPF(), validate_docbr.CNPJ()
        if values["type_entity"] == EntityTypeEnum.pj:
            if not cnpj.validate(v):
                raise ValueError("Invalid CNPJ")

            return "".join(filter(str.isdigit, v))

        if not cpf.validate(v):
            raise ValueError("Invalid CPF")

        return "".join(filter(str.isdigit, v))


class EntityCreate(Entity):
    password: str


class Charge(pydantic.BaseModel):
    class Config:
        orm_mode = True

    debtor: Entity
    creditor_cpf_cnpj: str
    debito: pydantic.PositiveFloat
    is_active: bool

    @pydantic.validator("creditor_cpf_cnpj")
    def validate_creditor_cpf_cnpj(cls, v, values):
        cpf, cnpj = validate_docbr.CPF(), validate_docbr.CNPJ()
        if not (cpf.validate(v) or cnpj.validate(v)):
            raise ValueError("Invalid CPF / CNPJ")

        if 'debtor' not in values:
            raise ValueError("Debtor not found")

        debtor_cpf_cnpj = values['debtor'].cpf_cnpj
        creditor_cpf_cnpj = ''.join(filter(str.isdigit, v))
        if debtor_cpf_cnpj == creditor_cpf_cnpj:
            raise ValueError("You can not add debt for yourself")

        return creditor_cpf_cnpj


class ChargeCreate(Charge):
    pass