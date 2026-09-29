from sqlalchemy.orm import InstrumentedAttribute

from app.db.session import SessionLocal
from app.models.product import Product
from sqlalchemy.orm import Session
from typing import Any, Callable


def _serialize_product(product: Product) -> dict[str, Any]:
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
    ##
    # @param item_key 検索対象のカラム名 (Productのマッピング済み属性名)
    # @param item_name 検索値
    # return 商品データ (見つからない場合は None)
    #
    products = db.query(Product).order_by(Product.product_id).all()
    return [_serialize_product(p) for p in products]


def get_product_point_item_tool(db: Session, item_key: str, item_name: str | int) -> dict | None:
    ##
    # @param item_key 検索対象のカラム名 (Productのマッピング済み属性名)
    # @param item_name 検索値
    # return 商品データ (見つからない場合は None)
    #
    column = getattr(Product, item_key, None)
    if not isinstance(column, InstrumentedAttribute):
        raise ValueError(f"invalid item_key: {item_key}")

    product = db.query(Product).filter(column == item_name).first()
    if product is None:
        return None

    return _serialize_product(product)


SEARCHABLE_COLUMNS = ["product_id", "name", "category", "rating", "stock_quantity", "price"]


## AI用使toolリスト
PRODUCT_TOOLS: list[dict[str, Any]] = [
    {
        "toolSpec": {
            "name": "list_products_tool",
            "description": "登録されている商品を全件取得する。",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                }
            },
        },
    },
    {
        "toolSpec": {
            "name": "get_product_point_item_tool",
            "description": "指定したカラム名とデータををもとにDBから検索する",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "item_key": {
                            "type": "string",
                            "description": "検索するテーブルのカラム名",
                            "enum": SEARCHABLE_COLUMNS,
                        },
                        "item_name": {
                            "type": "string",
                            "description": "検索対象の値"
                        }
                    },
                    "required": ["item_key", "item_name"],
                    "additionalProperties": False,
                }
            },
        },
    },
]

PRODUCT_TOOL_HANDLERS: dict[str, Callable[..., list[dict[str, Any]]]] = {
    "list_products_tool": lambda db, **kwargs: list_products_tool(db),
    "get_product_point_item_tool": lambda db, **kwargs: get_product_point_item_tool(db, **kwargs),
}

