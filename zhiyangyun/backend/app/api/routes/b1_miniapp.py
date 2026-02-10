from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.business import MiniappServiceRequestCreate
from app.services.business_service import BusinessService

router = APIRouter(prefix="/b1-miniapp", tags=["B1"])
service = BusinessService()


@router.get("/requests", response_model=ApiResponse)
def list_requests(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_requests(db, current.tenant_id))


@router.post("/requests", response_model=ApiResponse)
def create_request(payload: MiniappServiceRequestCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_request(db, current.tenant_id, payload))
