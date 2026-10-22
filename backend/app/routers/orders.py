from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Order, OrderItem, Product
from ..schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def list_orders(limit: int = Query(default=20, ge=1, le=200), db: Session = Depends(get_db)) -> list[Order]:
    query = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc(), Order.id.desc())
    return list(db.scalars(query.limit(limit)))


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> Order:
    """Create an order and decrement stock atomically; rejects the whole order if any line is short."""
    order = Order(customer=payload.customer)
    for line in payload.items:
        product = db.get(Product, line.product_id)
        if product is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Product {line.product_id} not found")
        if product.stock < line.quantity:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, f"Insufficient stock for {product.sku}")
        product.stock -= line.quantity
        order.items.append(OrderItem(product_id=product.id, quantity=line.quantity, unit_price=product.price))
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
