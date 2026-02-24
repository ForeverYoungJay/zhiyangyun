from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.oa import ShiftTemplateCreate, ShiftAssignmentCreate, ShiftAssignmentStatusUpdate
from app.services.oa_service import OAService

router = APIRouter(prefix="/oa1-shift", tags=["A2-OA1"])
service = OAService()


@router.get("/templates", response_model=ApiResponse)
def list_templates(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_shifts(db, current.tenant_id, page, page_size, keyword, status))


@router.post("/templates", response_model=ApiResponse)
def create_template(payload: ShiftTemplateCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_shift(db, current.tenant_id, payload))


@router.get("/assignments", response_model=ApiResponse)
def list_assignments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    shift_id: str = Query(default=""),
    user_id: str = Query(default=""),
    duty_date: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_assignments(db, current.tenant_id, page, page_size, keyword, status, shift_id, user_id, duty_date))


@router.post("/assignments", response_model=ApiResponse)
def create_assignment(payload: ShiftAssignmentCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_assignment(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assignments/{assignment_id}/status", response_model=ApiResponse)
def update_assignment_status(
    assignment_id: str,
    payload: ShiftAssignmentStatusUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    try:
        return ApiResponse(message="updated", data=service.update_assignment_status(db, current.tenant_id, assignment_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
