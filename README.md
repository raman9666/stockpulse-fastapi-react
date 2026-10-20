# StockPulse — Inventory & Sales Analytics (FastAPI + React)

![CI](https://github.com/raman9666/stockpulse-fastapi-react/actions/workflows/ci.yml/badge.svg)

A full-stack inventory and sales dashboard: a **FastAPI** backend for products, orders and analytics with **SQLAlchemy 2**, and a **React (Vite)** dashboard with KPI cards and SVG charts.

## Features
- Product catalog with SKU, category, price and stock; search and low-stock filter
- Order creation that validates and decrements stock in a single transaction (rejects short orders)
- Analytics endpoints: revenue summary, daily sales, top products, revenue by category
- Seeded demo data (30 days of orders) so the dashboard works out of the box
- React dashboard: KPI cards, daily revenue chart, category and top-product bars, low-stock alerts, recent orders, 7/14/30-day range switch
- OpenAPI docs at `/docs`, pytest tests, Dockerfile

## Tech stack
Python 3.12 · FastAPI · SQLAlchemy 2 · Pydantic v2 · SQLite (PostgreSQL-ready via `STOCKPULSE_DATABASE_URL`) · React 18 · Vite

## API
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/products` | List (`category`, `low_stock`, `search`) / create |
| PATCH | `/api/products/{id}` | Update product |
| GET/POST | `/api/orders` | Recent orders / create order |
| GET | `/api/analytics/summary?days=30` | Revenue, orders, AOV, low-stock count |
| GET | `/api/analytics/sales-by-day?days=14` | Daily revenue series |
| GET | `/api/analytics/top-products` | Best sellers by revenue |
| GET | `/api/analytics/revenue-by-category` | Category breakdown |

## Run locally
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload       # http://localhost:8000/docs
pytest

cd ../frontend
npm install
npm run dev                         # http://localhost:5173
```
