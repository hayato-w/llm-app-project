from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    model_config = {"from_attributes": True}
