from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.medical import MedicationOrderCreate, MedicationExecutionCreate
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/m4-medication", tags=["A1-M4"])
service = MedicalService()


@router.get("/orders", response_model=ApiResponse)
def list_orders(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_medication_orders(db, current.tenant_id))


@router.post("/orders", response_model=ApiResponse)
def create_order(payload: MedicationOrderCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_medication_order(db, current.tenant_id, payload))


@router.get("/executions", response_model=ApiResponse)
def list_exec(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_medication_executions(db, current.tenant_id))


@router.post("/executions", response_model=ApiResponse)
def create_exec(payload: MedicationExecutionCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_medication_execution(db, current.tenant_id, payload, current.user_id))
