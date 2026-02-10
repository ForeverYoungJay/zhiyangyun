from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.business import FamilyAccountCreate, FamilyVisitCreate
from app.services.business_service import BusinessService

router = APIRouter(prefix="/b2-family", tags=["B2"])
service = BusinessService()


@router.get("/accounts", response_model=ApiResponse)
def list_accounts(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_families(db, current.tenant_id))


@router.post("/accounts", response_model=ApiResponse)
def create_account(payload: FamilyAccountCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_family(db, current.tenant_id, payload))


@router.get("/visits", response_model=ApiResponse)
def list_visits(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_visits(db, current.tenant_id))


@router.post("/visits", response_model=ApiResponse)
def create_visit(payload: FamilyVisitCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_visit(db, current.tenant_id, payload))
