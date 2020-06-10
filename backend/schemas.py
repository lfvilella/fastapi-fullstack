import pydantic
import enum



class ClientEnum(str, enum.Enum):
    pj = 'pj'
    pf = 'pf'

class Client(pydantic.BaseModel):
    id: str
    name: str
    type_client: ClientEnum

    class Config:
        orm_mode = True
