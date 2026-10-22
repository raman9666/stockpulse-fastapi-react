"""Populate the database with realistic demo data so the dashboard has something to show."""
import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Order, OrderItem, Product

CATALOG = [
    ("ELC-1001", "Wireless Earbuds Pro", "Electronics", "59.99", 140),
    ("ELC-1002", "USB-C Fast Charger 65W", "Electronics", "34.50", 220),
    ("ELC-1003", "Smart Fitness Band", "Electronics", "79.00", 8),
    ("HOM-2001", "Ceramic Coffee Mug Set", "Home", "24.99", 90),
    ("HOM-2002", "LED Desk Lamp", "Home", "39.90", 6),
    ("HOM-2003", "Memory Foam Pillow", "Home", "29.00", 75),
    ("FIT-3001", "Yoga Mat Premium", "Fitness", "32.00", 60),
    ("FIT-3002", "Adjustable Dumbbells", "Fitness", "149.00", 4),
    ("OFF-4001", "Ergonomic Office Chair", "Office", "219.00", 25),
    ("OFF-4002", "Mechanical Keyboard", "Office", "89.00", 48),
]
CUSTOMERS = ["Acme Retail", "Bright Stores", "Nova Traders", "Urban Mart", "Peak Supplies", "Blue Ocean Co"]


def seed(db: Session, days: int = 30, rng: random.Random | None = None) -> None:
    if db.scalar(select(Product.id).limit(1)):
        return
    rng = rng or random.Random(42)
    products = [Product(sku=s, name=n, category=c, price=Decimal(p), stock=st) for s, n, c, p, st in CATALOG]
    db.add_all(products)
    db.flush()
    now = datetime.now()
    for day in range(days):
        for _ in range(rng.randint(2, 7)):
            created = now - timedelta(days=day, hours=rng.randint(0, 10))
            order = Order(customer=rng.choice(CUSTOMERS), created_at=created)
            for product in rng.sample(products, rng.randint(1, 3)):
                order.items.append(OrderItem(product_id=product.id, quantity=rng.randint(1, 4), unit_price=product.price))
            db.add(order)
    db.commit()
