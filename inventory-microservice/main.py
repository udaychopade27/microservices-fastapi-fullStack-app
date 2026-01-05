from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import Product
from deps import owner_required
from pydantic import BaseModel
from typing import List
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics import (
    inventory_requests,
    stock_reserved,
    stock_released,
    inventory_latency,
    http_requests_total, 
    http_request_latency_seconds
)
import time

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Service")

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

class PriceUpdate(BaseModel):
    price: float

class RefillRequest(BaseModel):
    qty: int

class Config:
    orm_mode = True
    
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    http_requests_total.labels(
        request.method,
        request.url.path,
        response.status_code
    ).inc()

    http_request_latency_seconds.labels(
        request.url.path
    ).observe(duration)

    return response

@app.get("/api/inventory/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/api/inventory/products")
def add_product(data: ProductCreate,
                db: Session = Depends(get_db),
                user=Depends(owner_required)):
    p = Product(name=data.name, price=data.price, stock=data.stock)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.put("/api/inventory/products/{pid}")
def update_price(pid: int,
                 data: PriceUpdate,
                 db: Session = Depends(get_db),
                 user=Depends(owner_required)):
    p = db.get(Product, pid)
    if not p:
        raise HTTPException(404)
    p.price = data.price
    db.commit()
    return p

@app.post(
    "/api/inventory/products/bulk",
    response_model=List[ProductResponse]
)
def add_products_bulk(
    products: List[ProductCreate],
    db: Session = Depends(get_db),
    user=Depends(owner_required)
):
    try:
        db_products = [
            Product(
                name=p.name,
                price=p.price,
                stock=p.stock
            )
            for p in products
        ]

        db.add_all(db_products)
        db.commit()

        # Ensure IDs are loaded
        for product in db_products:
            db.refresh(product)

        return db_products

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))



@app.post("/api/inventory/refill/{pid}")
def refill_stock(pid: int,
                 data: RefillRequest,
                 db: Session = Depends(get_db),
                 user=Depends(owner_required)):
    p = db.get(Product, pid)
    if not p:
        raise HTTPException(404)
    p.stock += data.qty
    db.commit()
    return p

@app.post("/api/inventory/reserve/{pid}")
def reserve_stock(pid: int, qty: int, db: Session = Depends(get_db)):
    p = db.get(Product, pid)

    if not p or p.stock < qty:
        return {"status": "out_of_stock"}

    p.stock -= qty
    db.commit()

    # PROMETHEUS
    stock_reserved.labels(str(pid)).inc(qty)

    return {
        "status": "reserved",
        "price": p.price
    }



@app.post("/api/inventory/release/{product_id}")
def release(product_id: int, qty: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404)

    product.stock += qty
    db.commit()

    # METRIC
    stock_released.labels(str(product_id)).inc(qty)

    return {"status": "released"}



@app.get("/api/inventory/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/inventory/health")
def health():
    return {"status": "inventory ok"}   
