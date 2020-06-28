Module app.data_access
======================
Data Access

This module is reponsible to handle all interactions to the database

Functions
---------

    
`check_api_key(db: sqlalchemy.orm.session.Session, api_key: str) ‑> app.models.APIKey`
:   Check API Key
    This method is used to verify API Key is valid
    
    Args:
        api_key (str): identifier.verifier e.g RaNdomString.Verifier
    
    Raises:
        APIKeyNotFound: The raises is not valid or not found error when API Key not exist.

    
`create_api_key(db: sqlalchemy.orm.session.Session, cpf_cnpj: str, persist=True) ‑> str`
:   

    
`create_charge(db: sqlalchemy.orm.session.Session, charge: app.schemas.ChargeCreate, api_key: str) ‑> app.models.Charge`
:   

    
`create_entity(db: sqlalchemy.orm.session.Session, entity: app.schemas.Entity, password: bool = None, persist: bool = True) ‑> app.models.Entity`
:   

    
`delete_api_key(db: sqlalchemy.orm.session.Session, api_key: str) ‑> app.models.APIKey`
:   

    
`entity_set_password(db: sqlalchemy.orm.session.Session, cpf_cnpj: str, password: str, entity: app.models.Entity = None, persist=True) ‑> app.models.Entity`
:   

    
`filter_charge(db: sqlalchemy.orm.session.Session, charge_filter: app.schemas.ChargeFilter, api_key: str) ‑> List[app.schemas.ChargeFullInfo]`
:   

    
`filter_entity_by_type(db: sqlalchemy.orm.session.Session, type_entity: str, api_key: str, limit: int = 100) ‑> List[app.models.Entity]`
:   

    
`generate_api_key(identifier, verifier) ‑> str`
:   

    
`get_charge_by_creditor_cpf_cnpj(db: sqlalchemy.orm.session.Session, creditor_cpf_cnpj: str) ‑> app.models.Charge`
:   

    
`get_charge_by_id(db: sqlalchemy.orm.session.Session, charge_id: str, api_key: str) ‑> app.models.Charge`
:   

    
`get_entity_api_key_by_id(db: sqlalchemy.orm.session.Session, api_key: str) ‑> app.models.APIKey`
:   

    
`get_entity_by_api_key(db: sqlalchemy.orm.session.Session, api_key: str) ‑> app.models.Entity`
:   

    
`get_entity_by_cpf_cnpj(db: sqlalchemy.orm.session.Session, cpf_cnpj: str, api_key: str = None, validate_api_key=True, raise_error=False) ‑> app.models.Entity`
:   

    
`get_entity_by_cpf_cnpj_and_password(db: sqlalchemy.orm.session.Session, cpf_cnpj: str, password: str) ‑> app.models.Entity`
:   

    
`payment_charge(db: sqlalchemy.orm.session.Session, payment_info: app.schemas.ChargePayment, api_key: str) ‑> app.models.Charge`
:   

    
`split_api_key(api_key: str) ‑> Tuple[str]`
:   

Classes
-------

`APIKeyNotFound(...)`
:   API Key Not Found
    
    This error is raised when the API Key string is not found in the database or is not valid

    ### Ancestors (in MRO)

    * app.data_access.DataAccessException
    * builtins.Exception
    * builtins.BaseException

`DataAccessException(...)`
:   Data Access Exception
    
    This error is raised when data passed to the function is not valid

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * app.data_access.APIKeyNotFound
    * app.data_access.DoesNotExisit
    * app.data_access.ValidationError

`DoesNotExisit(...)`
:   Data Access Exception
    
    This error is raised when data passed to the function is not valid

    ### Ancestors (in MRO)

    * app.data_access.DataAccessException
    * builtins.Exception
    * builtins.BaseException

`ValidationError(...)`
:   Data Access Exception
    
    This error is raised when data passed to the function is not valid

    ### Ancestors (in MRO)

    * app.data_access.DataAccessException
    * builtins.Exception
    * builtins.BaseException