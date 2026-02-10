from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.medical import VitalSignCreate, HealthAssessmentCreate
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/m6-health", tags=["A1-M6"])
service = MedicalService()


@router.get("/vitals", response_model=ApiResponse)
def list_vitals(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_vitals(db, current.tenant_id))


@router.post("/vitals", response_model=ApiResponse)
def create_vital(payload: VitalSignCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_vital(db, current.tenant_id, payload))


@router.get("/assessments", response_model=ApiResponse)
def list_assessments(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_assessments(db, current.tenant_id))


@router.post("/assessments", response_model=ApiResponse)
def create_assessment(payload: HealthAssessmentCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_assessment(db, current.tenant_id, payload))
