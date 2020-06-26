FORMAT: A1

# xyzCréditos

Open: http://xyzcreditos.lfvilella.com

This is an API about charges such as SERASA, obviously simpler.

I use to develop:
- Python
- Fastapi
- Sqlalchemy
- Docker / docker-compose
- VueJS

## To run locally
```
$ make build
$ make up
```

Open: http://localhost:80

Open API: http://localhost:8000/docs

# API Resources

All resources needs api_key except create_entity.

![alt text](https://github.com/lfvilella/xyzCredito-CCT/blob/master/images_readme/api_page.png?raw=true)
![alt text](https://github.com/lfvilella/xyzCredito-CCT/blob/master/images_readme/login_page.png?raw=true)
![alt text](https://github.com/lfvilella/xyzCredito-CCT/blob/master/images_readme/raw_frontend.png?raw=true)
![alt text](https://github.com/lfvilella/xyzCredito-CCT/blob/master/images_readme/searching_charge.png?raw=true)

## Entity collection [ /api/v.1/entity ]

### Filter entities by type [GET]
```
http://localhost:8000/api/v.1/entity?type_entity=<pf or pj>&api_key=<api_key_here>
```

- Successful Response 200 (application/json)
```
{
  "name": "string",
  "cpf_cnpj": "string",
  "type_entity": "pj"
}
```


### Create a entity [POST]
```
{
  "name": "string",
  "cpf_cnpj": "string",
  "password": "string"
}
```

- Successful Response 201 Created (application/json)
```
{
  "name": "string",
  "cpf_cnpj": "string",
  "type_entity": "pj"
}
```

### Read a entity [GET][ /api/v.1/entity/{cpf_cnpj} ]

- Successful Response 200 (application/json)
```
{
  "name": "string",
  "cpf_cnpj": "string",
  "type_entity": "pj"
}
```

## Charge collection [ /api/v.1/charge ]

### Filter charge by debtor_cpf_cnpj, creditor_cpf_cnpj, is_active
```
http://localhost:8000/api/v.1/entity?debtor_cpf_cnpj=<value>&creditor_cpf_cnpj=<value>&is_active<True or False>&api_key=<api_key_here>
```

- Successful Response 200 (application/json)
```
{
  "id": "string",
  "debtor_cpf_cnpj": "string",
  "creditor_cpf_cnpj": "string",
  "debito": 0,
  "is_active": true,
  "created_at": "2020-06-26T01:03:57.996Z",
  "payed_at": "2020-06-26T01:03:57.996Z"
}
```

### Create a charge [POST]
```
{
  "debtor": {
    "name": "string",
    "cpf_cnpj": "string"
  },
  "creditor_cpf_cnpj": "string",
  "debito": 0
}
```

- Successful Response 201 Created (application/json)
```
{
  "id": "string",
  "debtor_cpf_cnpj": "string",
  "creditor_cpf_cnpj": "string",
  "debito": 0,
  "is_active": true,
  "created_at": "2020-06-26T01:08:36.604Z",
  "payed_at": "2020-06-26T01:08:36.604Z"
}
```

### Read a charge [GET][ /api/v.1/charge/{charge_id} ]

- Successful Response 200 (application/json)
```
{
  "id": "string",
  "debtor_cpf_cnpj": "string",
  "creditor_cpf_cnpj": "string",
  "debito": 0,
  "is_active": true,
  "created_at": "2020-06-26T01:06:50.839Z",
  "payed_at": "2020-06-26T01:06:50.839Z"
}
```

### Payment a charge [POST][ /api/v.1/charge/payment ]
```
{
  "id": "string",
  "creditor_cpf_cnpj": "string"
}
```

- Successful Response 200 (application/json)
```
{
  "id": "string",
  "debtor_cpf_cnpj": "string",
  "creditor_cpf_cnpj": "string",
  "debito": 0,
  "is_active": true,
  "created_at": "2020-06-26T01:09:15.002Z",
  "payed_at": "2020-06-26T01:09:15.002Z"
}
```

## Authenticate collection [ /api/v.1/authenticate ]

### Authenticate Login [POST]
```
{
  "cpf_cnpj": "string",
  "password": "string",
  "set_cookie": false
}
```

- Successful Response 200 (application/json)
```
{
  "api_key": "string",
  "cpf_cnpj": "string"
}
```

### Authenticate Logout [DELETE]
```
http://localhost:8000/api/v.1/authenticate?api_key=<api_key_here>
```

- Successful Response 204 (application/json)