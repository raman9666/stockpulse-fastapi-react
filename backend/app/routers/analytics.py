from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Order, OrderItem, Product
from ..schemas import CategoryRevenue, DailySales, Summary, TopProduct

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

LINE_TOTAL = OrderItem.unit_price * OrderItem.quantity


def _since(days: int) -> datetime:
    return datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())


@router.get("/summary", response_model=Summary)
def summary(days: int = Query(default=30, ge=1, le=365), db: Session = Depends(get_db)) -> Summary:
    since = _since(days)
    revenue = db.scalar(
        select(func.coalesce(func.sum(LINE_TOTAL), 0)).select_from(OrderItem).join(Order).where(Order.created_at >= since)
    )
    orders = db.scalar(select(func.count(Order.id)).where(Order.created_at >= since)) or 0
    revenue = Decimal(str(revenue)).quantize(Decimal("0.01"))
    return Summary(
        revenue=revenue,
        orders=orders,
        average_order_value=(revenue / orders).quantize(Decimal("0.01")) if orders else Decimal("0.00"),
        products=db.scalar(select(func.count(Product.id))) or 0,
        low_stock=db.scalar(select(func.count(Product.id)).where(Product.stock <= settings.low_stock_threshold)) or 0,
    )


@router.get("/sales-by-day", response_model=list[DailySales])
def sales_by_day(days: int = Query(default=14, ge=1, le=365), db: Session = Depends(get_db)) -> list[DailySales]:
    day_col = func.date(Order.created_at)
    rows = db.execute(
        select(day_col, func.sum(LINE_TOTAL), func.count(func.distinct(Order.id)))
        .select_from(Order)
        .join(OrderItem)
        .where(Order.created_at >= _since(days))
        .group_by(day_col)
    ).all()
    by_day = {str(d): (Decimal(str(rev)), n) for d, rev, n in rows}
    result = []
    for offset in range(days):
        d = date.today() - timedelta(days=days - 1 - offset)
        rev, n = by_day.get(d.isoformat(), (Decimal("0"), 0))
        result.append(DailySales(day=d, revenue=rev.quantize(Decimal("0.01")), orders=n))
    return result


@router.get("/top-products", response_model=list[TopProduct])
def top_products(limit: int = Query(default=5, ge=1, le=50), db: Session = Depends(get_db)) -> list[TopProduct]:
    rows = db.execute(
        select(Product.id, Product.name, func.sum(OrderItem.quantity), func.sum(LINE_TOTAL))
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(LINE_TOTAL).desc())
        .limit(limit)
    ).all()
    return [
        TopProduct(product_id=pid, name=name, units=units, revenue=Decimal(str(rev)).quantize(Decimal("0.01")))
        for pid, name, units, rev in rows
    ]


@router.get("/revenue-by-category", response_model=list[CategoryRevenue])
def revenue_by_category(db: Session = Depends(get_db)) -> list[CategoryRevenue]:
    rows = db.execute(
        select(Product.category, func.sum(LINE_TOTAL))
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.category)
        .order_by(func.sum(LINE_TOTAL).desc())
    ).all()
    return [CategoryRevenue(category=c, revenue=Decimal(str(r)).quantize(Decimal("0.01"))) for c, r in rows]
