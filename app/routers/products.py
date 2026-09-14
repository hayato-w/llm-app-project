from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product as ProductModel
from app.schemas.product import Product, ProductCreate

router = APIRouter(prefix="/products", tags=["products"])


def _serialize_product(product: ProductModel) -> dict[str, Any]:
    return {
        "product_id": product.product_id,
        "name": product.name,
        "rating": product.rating,
        "comments": product.comments,
        "category": product.category,
        "stock_quantity": product.stock_quantity,
        "price": product.price,
    }


def list_products_tool(db: Session) -> list[dict[str, Any]]:
    products = db.query(ProductModel).order_by(ProductModel.product_id).all()
    return [_serialize_product(p) for p in products]


def get_products_by_category_tool(db: Session, category: str) -> list[dict[str, Any]]:
    products = (
        db.query(ProductModel)
        .filter(ProductModel.category == category)
        .order_by(ProductModel.product_id)
        .all()
    )
    return [_serialize_product(p) for p in products]


PRODUCT_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_products",
            "description": "登録されている商品を全件取得する。",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_products_by_category",
            "description": "指定したカテゴリに属する商品を取得する。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "検索したい商品のカテゴリ名",
                    },
                },
                "required": ["category"],
                "additionalProperties": False,
            },
        },
    },
]

PRODUCT_TOOL_HANDLERS: dict[str, Callable[..., list[dict[str, Any]]]] = {
    "list_products": lambda db, **kwargs: list_products_tool(db),
    "get_products_by_category": lambda db, **kwargs: get_products_by_category_tool(db, **kwargs),
}


@router.get("", response_model=list[Product])
def list_products(db: Session = Depends(get_db)) -> list[ProductModel]:
    return db.query(ProductModel).order_by(ProductModel.product_id).all()


@router.post("", response_model=Product, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductModel:
    product = ProductModel(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductModel:
    product = db.get(ProductModel, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    product = db.get(ProductModel, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
