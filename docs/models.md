Module app.models
=================

Classes
-------

`APIKey(**kwargs)`
:   The most base type
    
    A simple constructor that allows initialization from kwargs.
    
    Sets attributes on the constructed instance using the names and
    values in ``kwargs``.
    
    Only keys that are present as
    attributes of the instance's class are allowed. These could be,
    for example, any mapped columns or relationships.

    ### Ancestors (in MRO)

    * sqlalchemy.ext.declarative.api.Base

    ### Instance variables

    `cpf_cnpj`
    :

    `created_at`
    :

    `id`
    :

    `is_admin`
    :

    `verifier_hash`
    :

`Charge(**kwargs)`
:   The most base type
    
    A simple constructor that allows initialization from kwargs.
    
    Sets attributes on the constructed instance using the names and
    values in ``kwargs``.
    
    Only keys that are present as
    attributes of the instance's class are allowed. These could be,
    for example, any mapped columns or relationships.

    ### Ancestors (in MRO)

    * sqlalchemy.ext.declarative.api.Base

    ### Instance variables

    `created_at`
    :

    `creditor_cpf_cnpj`
    :

    `debito`
    :

    `debtor_cpf_cnpj`
    :

    `id`
    :

    `is_active`
    :

    `payed_at`
    :

`Entity(**kwargs)`
:   The most base type
    
    A simple constructor that allows initialization from kwargs.
    
    Sets attributes on the constructed instance using the names and
    values in ``kwargs``.
    
    Only keys that are present as
    attributes of the instance's class are allowed. These could be,
    for example, any mapped columns or relationships.

    ### Ancestors (in MRO)

    * sqlalchemy.ext.declarative.api.Base

    ### Instance variables

    `cpf_cnpj`
    :

    `hashed_password`
    :

    `name`
    :

    `type_entity`
    :