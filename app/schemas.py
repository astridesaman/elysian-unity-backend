from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class ProductBase(BaseModel):
    slug: str
    name: str
    description: Optional[str] = None
    price: int  # centimes
    image_url: Optional[str] = None
    is_preorder: bool = False
    min_preorder_qty: int = 0
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True


class OrderItemIn(BaseModel):
    product_id: int
    size: Optional[str] = None
    quantity: int


class OrderCreate(BaseModel):
    email: EmailStr
    items: List[OrderItemIn]


class OrderItemOut(BaseModel):
    product_id: int
    size: Optional[str]
    quantity: int
    unit_price: int

    class Config:
        orm_mode = True


class OrderOut(BaseModel):
    id: int
    email: EmailStr
    status: str
    total_amount: int
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True


class WaitlistIn(BaseModel):
    email: EmailStr
    product_id: int


class WaitlistOut(BaseModel):
    id: int
    email: EmailStr
    product_id: int
    created_at: datetime

    class Config:
        orm_mode = True
