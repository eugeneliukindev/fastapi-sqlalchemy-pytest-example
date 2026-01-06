from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str


class UserOut(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)
