from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.schemas.asset import BuildingCreate, FloorCreate, RoomCreate, BedCreate, BedUpdateStatus
from app.schemas.common import ApiResponse
from app.services.asset_service import AssetService

router = APIRouter(prefix="/assets", tags=["assets"])
service = AssetService()


@router.get("/buildings", response_model=ApiResponse)
def list_buildings(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.list_buildings(db, current.tenant_id)
    return ApiResponse(data=data)


@router.post("/buildings", response_model=ApiResponse)
def create_building(payload: BuildingCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        data = service.create_building(db, current.tenant_id, payload)
        return ApiResponse(message="created", data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/floors", response_model=ApiResponse)
def list_floors(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.list_floors(db, current.tenant_id)
    return ApiResponse(data=data)


@router.post("/floors", response_model=ApiResponse)
def create_floor(payload: FloorCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.create_floor(db, current.tenant_id, payload)
    return ApiResponse(message="created", data=data)


@router.get("/rooms", response_model=ApiResponse)
def list_rooms(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.list_rooms(db, current.tenant_id)
    return ApiResponse(data=data)


@router.post("/rooms", response_model=ApiResponse)
def create_room(payload: RoomCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.create_room(db, current.tenant_id, payload)
    return ApiResponse(message="created", data=data)


@router.get("/beds", response_model=ApiResponse)
def list_beds(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.list_beds(db, current.tenant_id)
    return ApiResponse(data=data)


@router.post("/beds", response_model=ApiResponse)
def create_bed(payload: BedCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.create_bed(db, current.tenant_id, payload)
    return ApiResponse(message="created", data=data)


@router.patch("/beds/{bed_id}/status", response_model=ApiResponse)
def update_bed_status(
    bed_id: str,
    payload: BedUpdateStatus,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    try:
        data = service.update_bed_status(db, current.tenant_id, bed_id, payload.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ApiResponse(message="updated", data=data)


@router.get("/occupancy-summary", response_model=ApiResponse)
def occupancy_summary(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.occupancy_summary(db, current.tenant_id)
    return ApiResponse(data=data)


@router.post("/beds/reconcile", response_model=ApiResponse)
def reconcile_bed_status(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.reconcile_bed_status(db, current.tenant_id)
    return ApiResponse(message="reconciled", data=data)
