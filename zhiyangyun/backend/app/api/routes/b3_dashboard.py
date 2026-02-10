from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.business import DashboardMetricCreate
from app.services.business_service import BusinessService

router = APIRouter(prefix="/b3-dashboard", tags=["B3"])
service = BusinessService()


@router.get("/metrics", response_model=ApiResponse)
def list_metrics(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_metrics(db, current.tenant_id))


@router.post("/metrics", response_model=ApiResponse)
def create_metric(payload: DashboardMetricCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_metric(db, current.tenant_id, payload))
