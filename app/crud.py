from sqlalchemy.orm import Session
from sqlalchemy import or_

from . import models, schemas
from .models import Product, Order, OrderItem, WaitlistEntry


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


def create_order_from_stripe(db, session):
    order = Order(
        stripe_session_id=session["id"],
        customer_email=session["customer_details"]["email"],
        amount=session["amount_total"] / 100,
        status="paid"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order

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


def get_product_by_identifier(db: Session, identifier: str | int):
    # si c'est un nombre → id, sinon → slug
    try:
        pid = int(identifier)
        return db.query(models.Product).filter(models.Product.id == pid).first()
    except ValueError:
        return db.query(models.Product).filter(models.Product.slug == identifier).first()

def create_order_from_cart(
    db: Session,
    email: str,
    items_raw: list[schemas.CartItemRaw],
    is_student: bool = False,
):
    # 1) calcul sous-total
    sub_total = 0
    items_resolved = []

    for raw in items_raw:
        product = get_product_by_identifier(db, raw.id)
        if not product or not product.active:
            raise ValueError(f"Produit {raw.id} indisponible")

        line_total = product.price * raw.qty
        sub_total += line_total
        items_resolved.append((product, raw))

    # 2) remise éventuelle (fêtes/étudiants)
    discount = 0
    if is_student and sub_total > 0:
        discount = int(sub_total * 0.20)  # 20 % en centimes

    sub_after = sub_total - discount

    # 3) livraison (logique alignée avec ton JS)
    if sub_after == 0:
        shipping = 0
    elif sub_after > 10000:  # 100€ → 10000 centimes
        shipping = 0
    else:
        shipping = 400  # 4€ => 400 centimes

    total = sub_after + shipping

    # 4) création Order
    db_order = models.Order(
        email=email,
        total_amount=total,
        status="pending",
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # 5) OrderItem
    for product, raw in items_resolved:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            size=raw.size,
            quantity=raw.qty,
            unit_price=product.price,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    return db_order, total
