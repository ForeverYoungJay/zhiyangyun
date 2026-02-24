from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.oa import TrainingCourseCreate, TrainingRecordActionPayload, TrainingRecordCreate
from app.services.oa_service import OAService

router = APIRouter(prefix="/oa4-training", tags=["A2-OA4"])
service = OAService()


@router.get("/users/suggest", response_model=ApiResponse)
def suggest_users(keyword: str = "", limit: int = 20, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.suggest_users(db, current.tenant_id, keyword=keyword, limit=limit))


@router.get("/courses", response_model=ApiResponse)
def list_courses(page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_courses(db, current.tenant_id, page=page, page_size=page_size, keyword=keyword, status=status))


@router.post("/courses", response_model=ApiResponse)
def create_course(payload: TrainingCourseCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_course(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/records", response_model=ApiResponse)
def list_records(page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", course_id: str = "", db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_records(db, current.tenant_id, page=page, page_size=page_size, keyword=keyword, status=status, course_id=course_id))


@router.post("/records", response_model=ApiResponse)
def create_record(payload: TrainingRecordCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_record(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/records/{record_id}/action", response_model=ApiResponse)
def action_record(record_id: str, payload: TrainingRecordActionPayload, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="updated", data=service.action_record(db, current.tenant_id, record_id, payload, current.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/courses/{course_id}/closure", response_model=ApiResponse)
def course_closure(course_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.course_closure_stats(db, current.tenant_id, course_id))
