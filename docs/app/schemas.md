Module app.schemas
==================

Classes
-------

`APIKey(*, api_key: str, cpf_cnpj: app.schemas.CpfOrCnpj)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Descendants

    * ?.APIKey

`Authenticate(*, cpf_cnpj: app.schemas.CpfOrCnpj, password: str, set_cookie: bool = False)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

`ChargeCreate(*, debtor: app.schemas.EntityBase, creditor_cpf_cnpj: app.schemas.CpfOrCnpj, debito: pydantic.types.PositiveFloat)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    ### Static methods

    `validate_creditor_cpf_cnpj(v, values)`
    :

`ChargeDatabase(*, id: str, debtor_cpf_cnpj: app.schemas.CpfOrCnpj, creditor_cpf_cnpj: app.schemas.CpfOrCnpj, debito: pydantic.types.PositiveFloat, is_active: bool, created_at: datetime.datetime, payed_at: datetime.datetime = None)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Descendants

    * ?.ChargeDatabase
    * ?.ChargeDatabase
    * ?.ChargeDatabase

    ### Class variables

    `Config`
    :

`ChargeFilter(*, debtor_cpf_cnpj: app.schemas.CpfOrCnpj = None, creditor_cpf_cnpj: app.schemas.CpfOrCnpj = None, is_active: bool = None)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

`ChargeFullInfo(*, id: str, debtor: app.schemas.Entity, creditor: app.schemas.Entity, debito: pydantic.types.PositiveFloat, is_active: bool, created_at: datetime.datetime, payed_at: datetime.datetime = None)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Descendants

    * ?.ChargeFullInfo

    ### Class variables

    `Config`
    :

`ChargePayment(*, id: str, creditor_cpf_cnpj: app.schemas.CpfOrCnpj)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

`CpfOrCnpj(...)`
:   str(object='') -> str
    str(bytes_or_buffer[, encoding[, errors]]) -> str
    
    Create a new string object from the given object. If encoding or
    errors is specified, then the object must expose a data buffer
    that will be decoded using the given encoding and error handler.
    Otherwise, returns the result of object.__str__() (if defined)
    or repr(object).
    encoding defaults to sys.getdefaultencoding().
    errors defaults to 'strict'.

    ### Ancestors (in MRO)

    * builtins.str

    ### Static methods

    `validate(v)`
    :

`Entity(*, name: str, cpf_cnpj: app.schemas.CpfOrCnpj, type_entity: app.schemas.EntityTypeEnum = None)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * app.schemas.EntityBase
    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Descendants

    * ?.Entity
    * ?.Entity
    * ?.Entity
    * ?.Entity
    * ?.Entity

    ### Class variables

    `Config`
    :

    ### Static methods

    `validate_type_entity(v, values)`
    :

`EntityBase(*, name: str, cpf_cnpj: app.schemas.CpfOrCnpj)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Descendants

    * app.schemas.Entity
    * app.schemas.EntityCreate

    ### Class variables

    `Config`
    :

`EntityCreate(*, name: str, cpf_cnpj: app.schemas.CpfOrCnpj, password: str)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * app.schemas.EntityBase
    * pydantic.main.BaseModel
    * pydantic.utils.Representation

`EntityTypeEnum(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `pf`
    :

    `pj`
    :