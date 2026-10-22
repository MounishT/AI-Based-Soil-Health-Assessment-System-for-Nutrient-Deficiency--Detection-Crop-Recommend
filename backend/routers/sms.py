"""
routers/sms.py
--------------
SMS/WhatsApp alert service (mock Twilio integration).
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["SMS"])


class SMSRequest(BaseModel):
    phone: str
    message: str
    alert_type: str = "soil_alert"


class SMSResponse(BaseModel):
    success: bool
    message: str
    sid: Optional[str] = None


@router.post("/sms/send", response_model=SMSResponse)
async def send_sms(req: SMSRequest):
    if not req.phone or len(req.phone) < 10:
        return SMSResponse(success=False, message="Invalid phone number.")

    import uuid
    mock_sid = f"SM{uuid.uuid4().hex[:32]}"

    print(f"[SMS SERVICE] To: {req.phone} | Type: {req.alert_type} | Message: {req.message}")

    return SMSResponse(
        success=True,
        message=f"Alert sent to {req.phone}",
        sid=mock_sid,
    )


class BulkSMSRequest(BaseModel):
    phones: list[str]
    message: str
    alert_type: str = "soil_alert"


@router.post("/sms/bulk", response_model=SMSResponse)
async def send_bulk_sms(req: BulkSMSRequest):
    sent = 0
    for phone in req.phones:
        if phone and len(phone) >= 10:
            sent += 1

    return SMSResponse(
        success=True,
        message=f"Alerts sent to {sent}/{len(req.phones)} recipients.",
    )
