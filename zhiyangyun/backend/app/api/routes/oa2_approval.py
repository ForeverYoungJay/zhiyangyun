from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.oa import ApprovalRequestCreate
from app.services.oa_service import OAService

router = APIRouter(prefix="/oa2-approval", tags=["A2-OA2"])
service = OAService()


@router.get("/requests", response_model=ApiResponse)
def list_requests(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_approvals(db, current.tenant_id))


@router.post("/requests", response_model=ApiResponse)
def create_request(payload: ApprovalRequestCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_approval(db, current.tenant_id, payload))
