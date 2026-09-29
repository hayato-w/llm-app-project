from typing import Any, Callable

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product as ProductModel
from app.schemas.product import Product, ProductCreate
from app.handler import ErrorHandler
import traceback

router = APIRouter(prefix="/products", tags=["products"])



@router.get("", response_model=list[Product])
def list_products(db: Session = Depends(get_db)) -> list[ProductModel]:
    try:
        return db.query(ProductModel).order_by(ProductModel.product_id).all()
    except Exception:
        error_trace = traceback.format_exc()
        raise ErrorHandler(
            status_code=500,
            title="Get All Product Error",
            detail=error_trace,
        )

@router.post("", response_model=Product, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductModel:
    try:
        product = ProductModel(**payload.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception:
        error_trace = traceback.format_exc()
        raise ErrorHandler(
            status_code=500,
            title="Create Product Error",
            detail=error_trace,
        )

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductModel:
    try:
        product = db.get(ProductModel, product_id)
    except Exception:
        error_trace = traceback.format_exc()
        raise ErrorHandler(
            status_code=500,
            title="Get Product Error",
            detail=error_trace,
        )
    if product is None:
        raise ErrorHandler(
            status_code=404,
            title="Product Not Found",
            detail=f"product_id={product_id} was not found",
        )
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    product = db.get(ProductModel, product_id)
    if product is None:
        raise ErrorHandler(
            status_code=404,
            title="Product Not Found",
            detail=f"product_id={product_id} was not found",
        )
    try:
        db.delete(product)
        db.commit()
    except Exception:
        error_trace = traceback.format_exc()
        raise ErrorHandler(
            status_code=500,
            title="Delete Product Error",
            detail=error_trace,
        )
