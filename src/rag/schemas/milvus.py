from pydantic import BaseModel


class MilvusClientSchema(BaseModel):
    host: str
    port: int
    user: str
    password: str
    db_name: str


