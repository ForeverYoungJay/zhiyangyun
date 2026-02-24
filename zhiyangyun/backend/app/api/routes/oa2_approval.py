from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.oa import ApprovalActionPayload, ApprovalRequestCreate
from app.services.oa_service import OAService

router = APIRouter(prefix="/oa2-approval", tags=["A2-OA2"])
service = OAService()


@router.get("/users/suggest", response_model=ApiResponse)
def suggest_users(keyword: str = "", limit: int = 20, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.suggest_users(db, current.tenant_id, keyword=keyword, limit=limit))


@router.get("/requests", response_model=ApiResponse)
def list_requests(page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", module: str = "", db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_approvals(db, current.tenant_id, page=page, page_size=page_size, keyword=keyword, status=status, module=module))


@router.post("/requests", response_model=ApiResponse)
def create_request(payload: ApprovalRequestCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_approval(db, current.tenant_id, payload, current.user_id))


@router.post("/requests/{request_id}/action", response_model=ApiResponse)
def action_request(request_id: str, payload: ApprovalActionPayload, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="updated", data=service.action_approval(db, current.tenant_id, request_id, payload, current.user_id))


@router.get("/requests/{request_id}/logs", response_model=ApiResponse)
def list_logs(request_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_approval_logs(db, current.tenant_id, request_id))
