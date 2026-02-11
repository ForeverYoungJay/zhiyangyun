from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.care import (
    ServiceItemCreate,
    ServiceItemStatusUpdate,
    CarePackageCreate,
    CarePackageStatusUpdate,
    CarePackageItemCreate,
    ElderPackageCreate,
    CarePackageAssignmentCreate,
    TaskGenerateRequest,
    TaskScanRequest,
    TaskSuperviseRequest,
    RoundTaskCreate,
    TaskIssueReportRequest,
    DeanReviewRequest,
    DispatchTasksRequest,
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


@router.patch("/items/{item_id}/status", response_model=ApiResponse)
def update_item_status(item_id: str, payload: ServiceItemStatusUpdate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    row = service.update_item_status(db, current.tenant_id, item_id, payload.status)
    if not row:
        raise HTTPException(status_code=404, detail="项目不存在")
    return ApiResponse(message="updated", data=row)


@router.delete("/items/{item_id}", response_model=ApiResponse)
def delete_item(item_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    ok = service.delete_item(db, current.tenant_id, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="项目不存在")
    return ApiResponse(message="deleted", data={"id": item_id})


@router.get("/packages", response_model=ApiResponse)
def list_packages(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_packages(db, current.tenant_id))


@router.post("/packages", response_model=ApiResponse)
def create_package(payload: CarePackageCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_package(db, current.tenant_id, payload))


@router.patch("/packages/{package_id}/status", response_model=ApiResponse)
def update_package_status(package_id: str, payload: CarePackageStatusUpdate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    row = service.update_package_status(db, current.tenant_id, package_id, payload.status)
    if not row:
        raise HTTPException(status_code=404, detail="项目包不存在")
    return ApiResponse(message="updated", data=row)


@router.post("/package-items", response_model=ApiResponse)
def create_package_item(payload: CarePackageItemCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_package_item(db, current.tenant_id, payload))


@router.post("/elder-packages", response_model=ApiResponse)
def subscribe(payload: ElderPackageCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.subscribe_elder_package(db, current.tenant_id, payload))


@router.post("/package-assignments", response_model=ApiResponse)
def assign_package(payload: CarePackageAssignmentCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.assign_package_to_caregiver(db, current.tenant_id, payload))


@router.get("/package-assignments", response_model=ApiResponse)
def list_assignments(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_assignments(db, current.tenant_id))


@router.get("/caregivers", response_model=ApiResponse)
def list_caregivers(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_caregivers(db, current.tenant_id))


@router.get("/tasks", response_model=ApiResponse)
def list_tasks(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_tasks(db, current.tenant_id))


@router.get("/tasks/board", response_model=ApiResponse)
def task_board(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.task_board(db, current.tenant_id))


@router.post("/tasks/generate", response_model=ApiResponse)
def generate_tasks(payload: TaskGenerateRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="generated", data=service.generate_tasks(db, current.tenant_id, payload))


@router.post("/tasks/dispatch", response_model=ApiResponse)
def dispatch_tasks(payload: DispatchTasksRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.dispatch_tasks(db, current.tenant_id, current.user_id, payload)
    if isinstance(data, dict) and data.get("error"):
        raise HTTPException(status_code=403, detail=data["error"])
    return ApiResponse(message="dispatched", data=data)


@router.post("/tasks/round", response_model=ApiResponse)
def create_round_task(payload: RoundTaskCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    row = service.create_round_task(db, current.tenant_id, current.user_id, payload)
    if not row:
        raise HTTPException(status_code=403, detail="无权限创建查房任务")
    return ApiResponse(message="created", data=row)


@router.post("/tasks/{task_id}/scan-in", response_model=ApiResponse)
def scan_in(task_id: str, payload: TaskScanRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="ok", data=service.scan_in(db, current.tenant_id, current.user_id, task_id, payload.qr_value))


@router.post("/tasks/{task_id}/scan-out", response_model=ApiResponse)
def scan_out(task_id: str, payload: TaskScanRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="ok", data=service.scan_out(db, current.tenant_id, task_id, payload.qr_value))


@router.post("/tasks/{task_id}/supervise", response_model=ApiResponse)
def supervise(task_id: str, payload: TaskSuperviseRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="ok", data=service.supervise(db, current.tenant_id, task_id, payload.score))


@router.post("/tasks/{task_id}/issues", response_model=ApiResponse)
def report_issue(task_id: str, payload: TaskIssueReportRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    row = service.report_issue(db, current.tenant_id, task_id, payload.photo_urls, payload.description, payload.report_to_dean)
    if not row:
        raise HTTPException(status_code=404, detail="任务不存在")
    return ApiResponse(message="reported", data=row)


@router.post("/tasks/{task_id}/dean-review", response_model=ApiResponse)
def dean_review(task_id: str, payload: DeanReviewRequest, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.dean_review(db, current.tenant_id, current.user_id, task_id, payload.approved, payload.note, payload.deduction_score)
    if isinstance(data, dict) and data.get("error"):
        raise HTTPException(status_code=403, detail=data["error"])
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return ApiResponse(message="reviewed", data=data)


@router.get("/caregivers/{caregiver_id}/performance", response_model=ApiResponse)
def get_performance(caregiver_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.get_performance(db, current.tenant_id, caregiver_id))
