import pydantic
import enum
import validate_docbr


class PersonTypeEnum(str, enum.Enum):
    pj = 'pj'
    pf = 'pf'


class Person(pydantic.BaseModel):
    class Config:
        orm_mode = True

    cpf_cnpj: str
    name: str
    type_person: PersonTypeEnum


    @validator('cpf_cnpj')
    def validate_cpf_cnpj(cls, v, values):
        breakpoint()
        cpf, cnpj = validate_docbr.CPF(), validate_docbr.CNPJ()

        if values['type_person'] == PersonTypeEnum.pj:
            if not cnpj.validate(v):
                raise ValueError('Invalid CNPJ')

            return cnpj.mask(v)

        if not cpf.validate(v):
            raise ValueError('Invalid CPF')

        return cpf.mask(v)


class PersonCreate(Person):
    password: str