from pydantic import BaseModel, ConfigDict


class PostOut(BaseModel):
    id: int
    title: str
    user_id: int
    model_config = ConfigDict(from_attributes=True)
