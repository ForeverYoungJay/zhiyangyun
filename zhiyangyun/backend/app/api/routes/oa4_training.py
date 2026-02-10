from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.oa import TrainingCourseCreate, TrainingRecordCreate
from app.services.oa_service import OAService

router = APIRouter(prefix="/oa4-training", tags=["A2-OA4"])
service = OAService()


@router.get("/courses", response_model=ApiResponse)
def list_courses(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_courses(db, current.tenant_id))


@router.post("/courses", response_model=ApiResponse)
def create_course(payload: TrainingCourseCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_course(db, current.tenant_id, payload))


@router.get("/records", response_model=ApiResponse)
def list_records(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_records(db, current.tenant_id))


@router.post("/records", response_model=ApiResponse)
def create_record(payload: TrainingRecordCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_record(db, current.tenant_id, payload))
