from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.oa import ShiftTemplateCreate, ShiftAssignmentCreate
from app.services.oa_service import OAService

router = APIRouter(prefix="/oa1-shift", tags=["A2-OA1"])
service = OAService()


@router.get("/templates", response_model=ApiResponse)
def list_templates(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_shifts(db, current.tenant_id))


@router.post("/templates", response_model=ApiResponse)
def create_template(payload: ShiftTemplateCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_shift(db, current.tenant_id, payload))


@router.get("/assignments", response_model=ApiResponse)
def list_assignments(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_assignments(db, current.tenant_id))


@router.post("/assignments", response_model=ApiResponse)
def create_assignment(payload: ShiftAssignmentCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_assignment(db, current.tenant_id, payload))
