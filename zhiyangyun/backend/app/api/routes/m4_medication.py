from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.medical import MedicationOrderCreate, MedicationExecutionCreate
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/m4-medication", tags=["A1-M4"])
service = MedicalService()


@router.get("/elders/suggest", response_model=ApiResponse)
def suggest_elders(
    keyword: str = Query(default=""),
    limit: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.suggest_elders(db, current.tenant_id, keyword, limit))


@router.get("/orders", response_model=ApiResponse)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    elder_id: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_medication_orders(db, current.tenant_id, page, page_size, keyword, status, elder_id))


@router.post("/orders", response_model=ApiResponse)
def create_order(payload: MedicationOrderCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_medication_order(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/executions", response_model=ApiResponse)
def list_exec(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_medication_executions(db, current.tenant_id))


@router.post("/executions", response_model=ApiResponse)
def create_exec(payload: MedicationExecutionCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_medication_execution(db, current.tenant_id, payload, current.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
