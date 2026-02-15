from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.medical import VitalSignCreate, HealthAssessmentCreate, AssessmentClosePayload
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/m6-health", tags=["A1-M6"])
service = MedicalService()


@router.get("/elders/suggest", response_model=ApiResponse)
def suggest_elders(
    keyword: str = Query(default=""),
    limit: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.suggest_elders(db, current.tenant_id, keyword, limit))


@router.get("/vitals", response_model=ApiResponse)
def list_vitals(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    abnormal_level: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_vitals(db, current.tenant_id, page, page_size, keyword, abnormal_level))


@router.post("/vitals", response_model=ApiResponse)
def create_vital(payload: VitalSignCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_vital(db, current.tenant_id, payload, current.user_id))


@router.get("/assessments", response_model=ApiResponse)
def list_assessments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_assessments(db, current.tenant_id, page, page_size, keyword, status))


@router.post("/assessments", response_model=ApiResponse)
def create_assessment(payload: HealthAssessmentCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_assessment(db, current.tenant_id, payload, current.user_id))


@router.post("/assessments/{assessment_id}/close", response_model=ApiResponse)
def close_assessment(
    assessment_id: str,
    payload: AssessmentClosePayload,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    try:
        return ApiResponse(message="closed", data=service.close_assessment(db, current.tenant_id, assessment_id, payload.note))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
