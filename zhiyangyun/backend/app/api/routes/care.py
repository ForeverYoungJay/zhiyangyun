from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.care import (
    ServiceItemCreate,
    CarePackageCreate,
    CarePackageItemCreate,
    ElderPackageCreate,
    TaskGenerateRequest,
    TaskScanRequest,
    TaskSuperviseRequest,
)
from app.services.care_service import CareService

router = APIRouter(prefix="/care", tags=["care"])
service = CareService()


@router.get("/items", response_model=ApiResponse)
def list_items(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_items(db, current.tenant_id))


@router.post("/items", response_model=ApiResponse)
def create_item(payload: ServiceItemCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_item(db, current.tenant_id, payload))


@router.get("/packages", response_model=ApiResponse)
def list_packages(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_packages(db, current.tenant_id))


@router.post("/packages", response_model=ApiResponse)
def create_package(payload: CarePackageCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_package(db, current.tenant_id, payload))


@router.post("/package-items", response_model=ApiResponse)
def create_package_item(payload: CarePackageItemCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_package_item(db, current.tenant_id, payload))


@router.post("/elder-packages", response_model=ApiResponse)
def subscribe(payload: ElderPackageCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.subscribe_elder_package(db, current.tenant_id, payload))


@router.get("/tasks", response_model=ApiResponse)
def list_tasks(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_tasks(db, current.tenant_id))


@router.post("/tasks/generate", response_model=ApiResponse)
def generate_tasks(payload: TaskGenerateRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="generated", data=service.generate_tasks(db, current.tenant_id, payload))


@router.post("/tasks/{task_id}/scan-in", response_model=ApiResponse)
def scan_in(task_id: str, payload: TaskScanRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="ok", data=service.scan_in(db, current.tenant_id, task_id, payload.qr_value))


@router.post("/tasks/{task_id}/scan-out", response_model=ApiResponse)
def scan_out(task_id: str, payload: TaskScanRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="ok", data=service.scan_out(db, current.tenant_id, task_id, payload.qr_value))


@router.post("/tasks/{task_id}/supervise", response_model=ApiResponse)
def supervise(task_id: str, payload: TaskSuperviseRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="ok", data=service.supervise(db, current.tenant_id, task_id, payload.score))
