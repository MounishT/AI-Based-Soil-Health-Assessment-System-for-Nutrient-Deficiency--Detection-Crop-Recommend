"""
routers/share.py
----------------
Share report functionality.
"""

import hashlib
import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(tags=["Share"])

_SHARE_STORE: Dict[str, Dict[str, Any]] = {}


class ShareRequest(BaseModel):
    soil_health_score: float
    health_band: str
    diagnosis: Dict[str, str]
    fertilizer_recommendation: list = []
    crop_ranking: list = []
    input_values: dict = {}


class ShareResponse(BaseModel):
    share_id: str
    share_url: str
    expires_in: str = "7 days"


@router.post("/share/create", response_model=ShareResponse)
async def create_share_link(req: ShareRequest):
    raw = json.dumps(req.model_dump(), sort_keys=True, default=str)
    share_id = hashlib.md5(raw.encode()).hexdigest()[:12]

    _SHARE_STORE[share_id] = req.model_dump()

    return ShareResponse(
        share_id=share_id,
        share_url=f"/share/{share_id}",
        expires_in="7 days",
    )


class SharedReport(BaseModel):
    share_id: str
    data: Dict[str, Any]


@router.get("/share/{share_id}", response_model=SharedReport)
async def get_shared_report(share_id: str):
    if share_id not in _SHARE_STORE:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Share link expired or not found.")

    return SharedReport(share_id=share_id, data=_SHARE_STORE[share_id])
