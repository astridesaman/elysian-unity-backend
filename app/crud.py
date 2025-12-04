from sqlalchemy.orm import Session
from . import models, schemas


# === Products ===
def get_products(db: Session):
    return db.query(models.Product).filter(models.Product.active == True).all()


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# === Orders ===
def create_order(db: Session, order_in: schemas.OrderCreate):
    # calcul du total
    total = 0
    items_db = []

    for item in order_in.items:
        product = get_product(db, item.product_id)
        if not product or not product.active:
            raise ValueError(f"Produit {item.product_id} indisponible")
        line_total = product.price * item.quantity
        total += line_total
        items_db.append((product, item))

    db_order = models.Order(
        email=order_in.email,
        total_amount=total,
        status="pending",
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # créer items
    for product, item in items_db:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            size=item.size,
            quantity=item.quantity,
            unit_price=product.price,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return db_order


def list_orders(db: Session):
    return db.query(models.Order).all()


# === Waitlist ===
def create_waitlist_entry(db: Session, entry: schemas.WaitlistIn):
    db_entry = models.WaitlistEntry(
        email=entry.email,
        product_id=entry.product_id,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry
