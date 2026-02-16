from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.medical import BillingItemCreate, BillingInvoiceCreate, BillingInvoiceGenerate, BillingInvoiceWriteoff, BillingInvoiceException
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/m7-billing", tags=["A1-M7"])
service = MedicalService()


@router.get("/items", response_model=ApiResponse)
def list_items(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    elder_id: str = Query(default=""),
    start_date: str = Query(default=""),
    end_date: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_billing_items(db, current.tenant_id, page, page_size, keyword, status, elder_id, start_date, end_date))


@router.post("/items", response_model=ApiResponse)
def create_item(payload: BillingItemCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_billing_item(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/invoices", response_model=ApiResponse)
def list_invoices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    elder_id: str = Query(default=""),
    period_month: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_invoices(db, current.tenant_id, page, page_size, keyword, status, elder_id, period_month))


@router.post("/invoices", response_model=ApiResponse)
def create_invoice(payload: BillingInvoiceCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_invoice(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/generate", response_model=ApiResponse)
def generate_invoice(payload: BillingInvoiceGenerate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="generated", data=service.generate_invoice(db, current.tenant_id, payload, current.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/{invoice_id}/writeoff", response_model=ApiResponse)
def writeoff_invoice(invoice_id: str, payload: BillingInvoiceWriteoff, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="written_off", data=service.writeoff_invoice(db, current.tenant_id, invoice_id, payload, current.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/{invoice_id}/exception", response_model=ApiResponse)
def exception_invoice(invoice_id: str, payload: BillingInvoiceException, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="handled", data=service.handle_invoice_exception(db, current.tenant_id, invoice_id, payload, current.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/invoices/{invoice_id}/events", response_model=ApiResponse)
def list_invoice_events(invoice_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_invoice_events(db, current.tenant_id, invoice_id))
