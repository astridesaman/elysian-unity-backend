from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)  # en centimes
    image_url = Column(String, nullable=True)
    is_preorder = Column(Boolean, default=False)
    min_preorder_qty = Column(Integer, default=0)
    active = Column(Boolean, default=True)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending / paid / cancelled / refunded
    total_amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    size = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
