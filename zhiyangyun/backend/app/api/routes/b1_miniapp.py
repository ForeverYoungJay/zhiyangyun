from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.business import MiniappServiceRequestCreate
from app.services.business_service import BusinessService

router = APIRouter(prefix="/b1-miniapp", tags=["B1"])
service = BusinessService()


@router.get("/requests", response_model=ApiResponse)
def list_requests(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    elder_id: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_requests(db, current.tenant_id, page, page_size, keyword, status, elder_id))


@router.post("/requests", response_model=ApiResponse)
def create_request(payload: MiniappServiceRequestCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_request(db, current.tenant_id, payload))


@router.post("/requests/{request_id}/status", response_model=ApiResponse)
def update_request_status(request_id: str, status: str = Query(...), db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="updated", data=service.update_request_status(db, current.tenant_id, request_id, status))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
