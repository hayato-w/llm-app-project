from typing import Any

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    rating: int = Field(ge=1, le=5)
    comments: list[Any] = Field(default_factory=list)
    category: str
    stock_quantity: int = Field(ge=0)
    price: int = Field(ge=0)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    product_id: int

    model_config = {"from_attributes": True}


class responseSchema(BaseModel):
    response: str
    