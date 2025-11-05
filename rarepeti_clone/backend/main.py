from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db


app = FastAPI(
    title="RarePeti Inspired Boutique",
    description="Elegant pet gastronomy storefront inspired by RarePeti.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    models.Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        crud.seed_defaults(db)


@app.get("/api/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/products", response_model=list[schemas.ProductRead], tags=["products"])
def list_products(db: Session = Depends(get_db)):
    return crud.list_products(db)


@app.post(
    "/api/products",
    response_model=schemas.ProductRead,
    status_code=status.HTTP_201_CREATED,
    tags=["products"],
)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, payload)


@app.get(
    "/api/products/{product_id}",
    response_model=schemas.ProductRead,
    tags=["products"],
)
def retrieve_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.patch(
    "/api/products/{product_id}",
    response_model=schemas.ProductRead,
    tags=["products"],
)
def update_product(
    product_id: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db)
):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.update_product(db, product, payload)


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete_product(db, product)


@app.get("/api/videos", response_model=list[schemas.VideoRead], tags=["videos"])
def list_videos(db: Session = Depends(get_db)):
    return crud.list_videos(db)


@app.post(
    "/api/videos",
    response_model=schemas.VideoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["videos"],
)
def create_video(payload: schemas.VideoCreate, db: Session = Depends(get_db)):
    if payload.product_id and not crud.get_product(db, payload.product_id):
        raise HTTPException(status_code=404, detail="Linked product not found")
    return crud.create_video(db, payload)


@app.get("/api/quotes", response_model=list[schemas.QuoteRead], tags=["quotes"])
def list_quotes(db: Session = Depends(get_db)):
    return crud.list_quotes(db)


@app.post(
    "/api/quotes",
    response_model=schemas.QuoteRead,
    status_code=status.HTTP_201_CREATED,
    tags=["quotes"],
)
def create_quote(payload: schemas.QuoteCreate, db: Session = Depends(get_db)):
    return crud.create_quote(db, payload)

