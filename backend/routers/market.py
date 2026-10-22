"""
routers/market.py
-----------------
Mock market price API for crop prices.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(tags=["Market"])

MOCK_PRICES = {
    "Rice": {"price": 28, "unit": "kg", "market": "Mandi"},
    "Wheat": {"price": 22, "unit": "kg", "market": "Mandi"},
    "Maize": {"price": 19, "unit": "kg", "market": "Mandi"},
    "Cotton": {"price": 65, "unit": "kg", "market": "Mandi"},
    "Sugarcane": {"price": 3.5, "unit": "kg", "market": "Mandi"},
    "Tomato": {"price": 18, "unit": "kg", "market": "Mandi"},
    "Potato": {"price": 15, "unit": "kg", "market": "Mandi"},
    "Onion": {"price": 20, "unit": "kg", "market": "Mandi"},
    "Soybean": {"price": 42, "unit": "kg", "market": "Mandi"},
    "Groundnut": {"price": 55, "unit": "kg", "market": "Mandi"},
    "Chilli": {"price": 120, "unit": "kg", "market": "Mandi"},
    "Turmeric": {"price": 95, "unit": "kg", "market": "Mandi"},
    "Banana": {"price": 35, "unit": "kg", "market": "Mandi"},
    "Mango": {"price": 40, "unit": "kg", "market": "Mandi"},
    "Grapes": {"price": 60, "unit": "kg", "market": "Mandi"},
}


class CropPrice(BaseModel):
    crop: str
    price: float
    unit: str
    market: str


class MarketResponse(BaseModel):
    prices: List[CropPrice]
    source: str = "Mock Market Data"


@router.get("/market/prices", response_model=MarketResponse)
async def get_market_prices():
    prices = [CropPrice(crop=crop, **info) for crop, info in MOCK_PRICES.items()]
    return MarketResponse(prices=prices)


@router.get("/market/prices/{crop}", response_model=CropPrice)
async def get_crop_price(crop: str):
    key = crop.title()
    if key in MOCK_PRICES:
        return CropPrice(crop=key, **MOCK_PRICES[key])
    return CropPrice(crop=key, price=0, unit="kg", market="N/A")
