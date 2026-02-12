from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.commerce import (
    CategoryCreate,
    InventoryChangeCreate,
    InventoryCheckCreate,
    OrderActionCreate,
    OrderCreate,
    SkuCreate,
    SpuCreate,
    SpuStatusUpdate,
)
from app.services.commerce_service import CommerceService

router = APIRouter(prefix="/shop", tags=["商城+库存"])
service = CommerceService()


@router.get("/categories", response_model=ApiResponse)
def list_categories(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_categories(db, current.tenant_id))


@router.post("/categories", response_model=ApiResponse)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_category(db, current.tenant_id, payload))


@router.get("/spu", response_model=ApiResponse)
def list_spu(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_spu(db, current.tenant_id, page, page_size, keyword))


@router.post("/spu", response_model=ApiResponse)
def create_spu(payload: SpuCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_spu(db, current.tenant_id, payload))


@router.patch("/spu/{spu_id}/status", response_model=ApiResponse)
def update_spu_status(spu_id: str, payload: SpuStatusUpdate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(data=service.update_spu_status(db, current.tenant_id, spu_id, payload.status))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sku", response_model=ApiResponse)
def list_sku(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_sku(db, current.tenant_id, page, page_size, keyword))


@router.get("/sku/suggest", response_model=ApiResponse)
def suggest_sku(
    keyword: str = Query(default=""),
    limit: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.suggest_sku(db, current.tenant_id, keyword, limit))


@router.post("/sku", response_model=ApiResponse)
def create_sku(payload: SkuCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_sku(db, current.tenant_id, payload))


@router.post("/inventory/in", response_model=ApiResponse)
def stock_in(payload: InventoryChangeCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(data=service.stock_in(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/inventory/out", response_model=ApiResponse)
def stock_out(payload: InventoryChangeCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(data=service.stock_out(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/inventory/check", response_model=ApiResponse)
def stock_check(payload: InventoryCheckCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(data=service.stock_check(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/inventory/ledger", response_model=ApiResponse)
def inventory_ledger(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sku_id: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_inventory_ledger(db, current.tenant_id, page, page_size, sku_id))


@router.get("/inventory/warnings", response_model=ApiResponse)
def inventory_warnings(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_warnings(db, current.tenant_id))


@router.get("/orders", response_model=ApiResponse)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_orders(db, current.tenant_id, page, page_size, keyword, status))


@router.post("/orders", response_model=ApiResponse)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_order(db, current.tenant_id, payload))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/pay", response_model=ApiResponse)
def pay_order(order_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(data=service.pay_order(db, current.tenant_id, order_id))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/cancel", response_model=ApiResponse)
def cancel_order(order_id: str, payload: OrderActionCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(data=service.cancel_order(db, current.tenant_id, order_id, payload.reason))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/refund", response_model=ApiResponse)
def refund_order(order_id: str, payload: OrderActionCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(data=service.refund_order(db, current.tenant_id, order_id, payload.reason))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/complete", response_model=ApiResponse)
def complete_order(order_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(data=service.complete_order(db, current.tenant_id, order_id))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/elders/{elder_id}/account-ledger", response_model=ApiResponse)
def elder_account_ledger(elder_id: str, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_account_ledger(db, current.tenant_id, elder_id))
