Module app.api
==============

Functions
---------

    
`authenticate_login(response: starlette.responses.Response, login: app.schemas.Authenticate, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`authenticate_logout(request: starlette.requests.Request, api_key: str = None, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`charge_payment(request: starlette.requests.Request, payment_info: app.schemas.ChargePayment, api_key: str = None, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`create_charge(request: starlette.requests.Request, charge: app.schemas.ChargeCreate, api_key: str = None, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`create_entity(entity: app.schemas.EntityCreate, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`filter_charge(request: starlette.requests.Request, debtor_cpf_cnpj: app.schemas.CpfOrCnpj = None, creditor_cpf_cnpj: app.schemas.CpfOrCnpj = None, is_active: bool = None, api_key: str = None, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`filter_entity(type_entity: app.schemas.EntityTypeEnum = None, limit: int = 100, api_key: str = None, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`get_api_key_from_request(request: starlette.requests.Request)`
:   

    
`get_db()`
:   

    
`handle_data_access_error(request: starlette.requests.Request, exception: app.data_access.DataAccessException)`
:   

    
`read_charge(charge_id: str, api_key: str = None, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`read_entity(cpf_cnpj: app.schemas.CpfOrCnpj, api_key: str = None, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
:   

    
`read_entity_logged(request: starlette.requests.Request, api_key: str = None, db: sqlalchemy.orm.session.Session = <fastapi.params.Depends object>)`
: