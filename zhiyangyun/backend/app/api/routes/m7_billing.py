from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.medical import BillingItemCreate, BillingInvoiceCreate
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/m7-billing", tags=["A1-M7"])
service = MedicalService()


@router.get("/items", response_model=ApiResponse)
def list_items(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_billing_items(db, current.tenant_id))


@router.post("/items", response_model=ApiResponse)
def create_item(payload: BillingItemCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_billing_item(db, current.tenant_id, payload))


@router.get("/invoices", response_model=ApiResponse)
def list_invoices(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_invoices(db, current.tenant_id))


@router.post("/invoices", response_model=ApiResponse)
def create_invoice(payload: BillingInvoiceCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_invoice(db, current.tenant_id, payload))
