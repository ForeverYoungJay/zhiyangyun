from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.business import FamilyAccountCreate, FamilyVisitCreate, FamilySurveyCreate, FamilyServiceOrderCreate
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


@router.get("/elders/{elder_id}/bills", response_model=ApiResponse)
def elder_bills(elder_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_family_bills(db, current.tenant_id, elder_id))


@router.get("/elders/{elder_id}/care-records", response_model=ApiResponse)
def elder_care_records(elder_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_family_care_records(db, current.tenant_id, elder_id))


@router.get("/elders/{elder_id}/overview", response_model=ApiResponse)
def elder_overview(elder_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    data = service.get_family_elder_overview(db, current.tenant_id, elder_id)
    if not data:
        return ApiResponse(code=404, message="长者不存在", data=None)
    return ApiResponse(data=data)


@router.get("/services/catalog", response_model=ApiResponse)
def service_catalog(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_service_catalog(db, current.tenant_id))


@router.post("/services/order", response_model=ApiResponse)
def service_order(payload: FamilyServiceOrderCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_family_service_order(db, current.tenant_id, payload))


@router.get("/surveys", response_model=ApiResponse)
def list_surveys(elder_id: str | None = None, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_surveys(db, current.tenant_id, elder_id))


@router.post("/surveys", response_model=ApiResponse)
def create_survey(payload: FamilySurveyCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_survey(db, current.tenant_id, payload))
