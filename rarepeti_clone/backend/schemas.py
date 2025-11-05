from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class QuoteBase(BaseModel):
    text: str = Field(..., min_length=3)
    author: Optional[str] = Field(default=None, max_length=120)


class QuoteCreate(QuoteBase):
    pass


class QuoteRead(QuoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoBase(BaseModel):
    title: str = Field(..., min_length=2)
    url: HttpUrl
    description: Optional[str] = Field(default=None, max_length=400)
    product_id: Optional[int] = None


class VideoCreate(VideoBase):
    pass


class VideoRead(VideoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)
    image_url: Optional[HttpUrl] = None
    category: Optional[str] = Field(default=None, max_length=100)
    available: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, min_length=10)
    price: Optional[float] = Field(default=None, gt=0)
    image_url: Optional[HttpUrl] = None
    category: Optional[str] = Field(default=None, max_length=100)
    available: Optional[bool] = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    videos: list[VideoRead] = []

    model_config = ConfigDict(from_attributes=True)


class ManyProducts(BaseModel):
    items: list[ProductRead]


class ManyVideos(BaseModel):
    items: list[VideoRead]


class ManyQuotes(BaseModel):
    items: list[QuoteRead]

