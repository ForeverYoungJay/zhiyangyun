from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.medical import MealPlanCreate, MealOrderCreate
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/m5-meal", tags=["A1-M5"])
service = MedicalService()


@router.get("/elders/suggest", response_model=ApiResponse)
def suggest_elders(
    keyword: str = Query(default=""),
    limit: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.suggest_elders(db, current.tenant_id, keyword, limit))


@router.get("/plans", response_model=ApiResponse)
def list_plans(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    meal_type: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_meal_plans(db, current.tenant_id, page, page_size, keyword, meal_type))


@router.post("/plans", response_model=ApiResponse)
def create_plan(payload: MealPlanCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_meal_plan(db, current.tenant_id, payload))


@router.get("/orders", response_model=ApiResponse)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status: str = Query(default=""),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return ApiResponse(data=service.list_meal_orders(db, current.tenant_id, page, page_size, keyword, status))


@router.post("/orders", response_model=ApiResponse)
def create_order(payload: MealOrderCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_meal_order(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
