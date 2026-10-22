"""
routers/profit.py
-----------------
Profit calculator for farming operations.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Profit"])

CROP_YIELD_ACRES = {
    "Rice": {"yield_kg": 2000, "cost_per_acre": 25000, "price_per_kg": 28},
    "Wheat": {"yield_kg": 1800, "cost_per_acre": 20000, "price_per_kg": 22},
    "Maize": {"yield_kg": 2200, "cost_per_acre": 18000, "price_per_kg": 19},
    "Cotton": {"yield_kg": 500, "cost_per_acre": 35000, "price_per_kg": 65},
    "Tomato": {"yield_kg": 8000, "cost_per_acre": 40000, "price_per_kg": 18},
    "Potato": {"yield_kg": 10000, "cost_per_acre": 30000, "price_per_kg": 15},
    "Soybean": {"yield_kg": 1200, "cost_per_acre": 15000, "price_per_kg": 42},
    "Groundnut": {"yield_kg": 1000, "cost_per_acre": 22000, "price_per_kg": 55},
    "Chilli": {"yield_kg": 800, "cost_per_acre": 45000, "price_per_kg": 120},
    "Turmeric": {"yield_kg": 2500, "cost_per_acre": 35000, "price_per_kg": 95},
}


class ProfitRequest(BaseModel):
    farm_size_acres: float
    crop_type: str = "Rice"
    custom_cost: Optional[float] = None
    custom_yield: Optional[float] = None
    custom_price: Optional[float] = None


class ProfitResponse(BaseModel):
    farm_size_acres: float
    crop_type: str
    estimated_cost: float
    expected_yield_kg: float
    expected_revenue: float
    estimated_profit: float
    cost_per_acre: float
    revenue_per_acre: float
    profit_per_acre: float
    roi_percent: float


@router.post("/profit/calculate", response_model=ProfitResponse)
async def calculate_profit(req: ProfitRequest):
    crop_key = req.crop_type.title()
    defaults = CROP_YIELD_ACRES.get(crop_key, {"yield_kg": 2000, "cost_per_acre": 25000, "price_per_kg": 25})

    cost_per_acre = req.custom_cost if req.custom_cost else defaults["cost_per_acre"]
    yield_kg = req.custom_yield if req.custom_yield else defaults["yield_kg"]
    price_kg = req.custom_price if req.custom_price else defaults["price_per_kg"]

    total_cost = cost_per_acre * req.farm_size_acres
    total_yield = yield_kg * req.farm_size_acres
    total_revenue = total_yield * price_kg
    profit = total_revenue - total_cost

    return ProfitResponse(
        farm_size_acres=req.farm_size_acres,
        crop_type=crop_key,
        estimated_cost=round(total_cost, 2),
        expected_yield_kg=round(total_yield, 2),
        expected_revenue=round(total_revenue, 2),
        estimated_profit=round(profit, 2),
        cost_per_acre=cost_per_acre,
        revenue_per_acre=round(yield_kg * price_kg, 2),
        profit_per_acre=round((yield_kg * price_kg) - cost_per_acre, 2),
        roi_percent=round(((profit / total_cost) * 100) if total_cost > 0 else 0, 1),
    )
