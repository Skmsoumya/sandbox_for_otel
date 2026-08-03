from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(default=0, ge=0)


class Item(BaseModel):
    id: int
    name: str
    quantity: int