from sqlalchemy import CheckConstraint, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

JSONVariant = JSON().with_variant(JSONB, "postgresql")


class Product(Base):
    """ECサイトの商品を表すテーブル。"""

    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_products_rating_range"),
        CheckConstraint("stock_quantity >= 0", name="ck_products_stock_quantity_non_negative"),
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
    )

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comments: Mapped[list | dict] = mapped_column(JSONVariant, nullable=False, default=list)
    category: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
