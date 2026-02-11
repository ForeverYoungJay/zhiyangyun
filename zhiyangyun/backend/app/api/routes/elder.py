from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.elder import LeadCreate, ElderCreate, ElderAdmit, ElderTransfer, ElderDischarge
from app.services.elder_service import ElderService

router = APIRouter(prefix="/elders", tags=["elders"])
service = ElderService()


@router.get("/leads", response_model=ApiResponse)
def list_leads(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_leads(db, current.tenant_id))


@router.post("/leads", response_model=ApiResponse)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_lead(db, current.tenant_id, payload))


@router.get("", response_model=ApiResponse)
def list_elders(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_elders(db, current.tenant_id))


@router.post("", response_model=ApiResponse)
def create_elder(payload: ElderCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_elder(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{elder_id}/admit", response_model=ApiResponse)
def admit(elder_id: str, payload: ElderAdmit, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.admit(db, current.tenant_id, elder_id, payload)
    return ApiResponse(message="admitted" if data else "failed", data=data)


@router.post("/{elder_id}/transfer", response_model=ApiResponse)
def transfer(elder_id: str, payload: ElderTransfer, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.transfer(db, current.tenant_id, elder_id, payload)
    return ApiResponse(message="transferred" if data else "failed", data=data)


@router.post("/{elder_id}/discharge", response_model=ApiResponse)
def discharge(elder_id: str, payload: ElderDischarge, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.discharge(db, current.tenant_id, elder_id, payload)
    return ApiResponse(message="discharged" if data else "failed", data=data)


@router.get("/{elder_id}/logs", response_model=ApiResponse)
def logs(elder_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.logs(db, current.tenant_id, elder_id))
