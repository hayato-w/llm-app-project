from app.db.session import SessionLocal
from app.models.product import Product


def get_product_item_data(item_name: str) -> dict | None:
    ##
    # @param item_name 商品名
    # return 商品データ (見つからない場合は None)
    #
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.name == item_name).first()
        if product is None:
            return None

        return {
            "product_id": product.product_id,
            "name": product.name,
            "rating": product.rating,
            "comments": product.comments,
            "category": product.category,
        }
    finally:
        db.close()


def get_product_item_class(category: str) -> list[dict]:
    ##
    # @param category 商品分類
    # return 同じ商品分類の商品データ一覧
    #
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.category == category).all()
        return [
            {
                "product_id": product.product_id,
                "name": product.name,
                "rating": product.rating,
                "comments": product.comments,
                "category": product.category,
            }
            for product in products
        ]
    finally:
        db.close()


def get_product_item_rating(rating: int) -> list[dict]:
    ##
    # @param rating 評価 (1〜5)
    # return 指定した評価の商品データ一覧
    #
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.rating == rating).all()
        return [
            {
                "product_id": product.product_id,
                "name": product.name,
                "rating": product.rating,
                "comments": product.comments,
                "category": product.category,
            }
            for product in products
        ]
    finally:
        db.close()
