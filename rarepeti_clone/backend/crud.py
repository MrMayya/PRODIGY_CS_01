from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from . import models, schemas


def list_products(db: Session) -> Sequence[models.Product]:
    stmt = (
        select(models.Product)
        .options(selectinload(models.Product.videos))
        .order_by(models.Product.created_at.desc())
    )
    return db.scalars(stmt).all()


def get_product(db: Session, product_id: int) -> models.Product | None:
    stmt = (
        select(models.Product)
        .options(selectinload(models.Product.videos))
        .where(models.Product.id == product_id)
    )
    return db.scalar(stmt)


def create_product(db: Session, payload: schemas.ProductCreate) -> models.Product:
    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: models.Product, payload: schemas.ProductUpdate) -> models.Product:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: models.Product) -> None:
    db.delete(product)
    db.commit()


def list_videos(db: Session) -> Sequence[models.Video]:
    stmt = select(models.Video).order_by(models.Video.created_at.desc())
    return db.scalars(stmt).all()


def create_video(db: Session, payload: schemas.VideoCreate) -> models.Video:
    video = models.Video(**payload.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def list_quotes(db: Session) -> Sequence[models.Quote]:
    stmt = select(models.Quote).order_by(models.Quote.created_at.desc())
    return db.scalars(stmt).all()


def create_quote(db: Session, payload: schemas.QuoteCreate) -> models.Quote:
    quote = models.Quote(**payload.model_dump())
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def seed_defaults(db: Session) -> None:
    if db.query(models.Product).count():
        return

    starter_products: Iterable[dict[str, object]] = [
        {
            "name": "Gourmet Salmon Feast",
            "description": "Premium wild-caught salmon bites crafted for discerning pets with a taste for the ocean.",
            "price": 19.99,
            "category": "Signature Meals",
            "image_url": "https://images.unsplash.com/photo-1514516430032-7a48eee34a30",
        },
        {
            "name": "Wholesome Harvest Bowl",
            "description": "Nutrient-rich medley of farm-fresh veggies and ethically sourced proteins for everyday vitality.",
            "price": 15.5,
            "category": "Daily Delights",
            "image_url": "https://images.unsplash.com/photo-1615937677800-8e1e65476f4c",
        },
        {
            "name": "Velvet Morning Treats",
            "description": "Slow-baked breakfast biscuits infused with calming chamomile and honey.",
            "price": 9.75,
            "category": "Treats",
            "image_url": "https://images.unsplash.com/photo-1558944351-c45873e4c0fa",
        },
    ]

    starter_quotes = [
        {
            "text": "Crafted with patience, served with love, savored in every wag.",
            "author": "RarePeti Atelier",
        },
        {
            "text": "When ingredients are honest, tails tell the story.",
            "author": "Founder, Maison RarePeti",
        },
        {
            "text": "Cuisine for companions who deserve more than ordinary bowls.",
            "author": None,
        },
    ]

    starter_videos = [
        {
            "title": "Inside the RarePeti Kitchen",
            "url": "https://www.youtube.com/watch?v=2LhoCfjm8R4",
            "description": "See how our chefs craft small-batch meals with meticulous care.",
        },
        {
            "title": "Sourcing Ingredients Sustainably",
            "url": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
            "description": "Follow our journey from local farms to pet tables.",
        },
    ]

    for product in starter_products:
        db.add(models.Product(**product))

    for quote in starter_quotes:
        db.add(models.Quote(**quote))

    for video in starter_videos:
        db.add(models.Video(**video))

    db.commit()

