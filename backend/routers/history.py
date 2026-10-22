from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import User, SoilReport
from backend.schemas import PaginatedHistoryResponse, SoilReportResponse

router = APIRouter(prefix="/history", tags=["History"])

@router.get("", response_model=PaginatedHistoryResponse)
def get_history(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve paginated history of soil analysis reports for the authenticated user.
    """
    query = db.query(SoilReport).filter(SoilReport.user_id == current_user.id)
    total = query.count()
    items = query.order_by(desc(SoilReport.created_at)).offset(offset).limit(limit).all()

    return PaginatedHistoryResponse(
        items=[
            SoilReportResponse.model_validate(item) for item in items
        ],
        total=total
    )

@router.get("/{report_id}", response_model=SoilReportResponse)
def get_history_detail(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve full details for a single historical report, with ownership checks.
    """
    report = db.query(SoilReport).filter(SoilReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    if report.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this report")
        
    return SoilReportResponse.model_validate(report)
