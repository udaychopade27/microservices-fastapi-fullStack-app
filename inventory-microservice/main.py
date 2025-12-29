from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import Product
from deps import owner_required
from pydantic import BaseModel
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Service")

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int

class PriceUpdate(BaseModel):
    price: float

class RefillRequest(BaseModel):
    qty: int

@app.get("/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/products")
def add_product(data: ProductCreate,
                db: Session = Depends(get_db),
                user=Depends(owner_required)):
    p = Product(name=data.name, price=data.price, stock=data.stock)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.put("/products/{pid}")
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

@app.post("/products/bulk")
def add_products_bulk(
    products: List[ProductCreate],
    db: Session = Depends(get_db),
    user=Depends(owner_required)
):
    created = []

    for p in products:
        product = Product(
            name=p.name,
            price=p.price,
            stock=p.stock
        )
        db.add(product)
        created.append(product)

    db.commit()
    return created


@app.post("/refill/{pid}")
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

@app.post("/reserve/{pid}")
def reserve_stock(pid: int, qty: int, db: Session = Depends(get_db)):
    p = db.get(Product, pid)
    if p.stock < qty:
        return {"status": "out_of_stock"}
    p.stock -= qty
    db.commit()
    return {
        "status": "reserved",
        "price": p.price
    }



@app.post("/release/{product_id}")
def release(product_id: int, qty: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404)

    product.stock += qty
    db.commit()

    return {"status": "released"}


@app.get("/health")
def health():
    return {"status": "inventory ok"}   
