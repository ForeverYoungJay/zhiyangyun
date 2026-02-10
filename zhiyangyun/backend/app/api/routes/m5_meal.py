from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.medical import MealPlanCreate, MealOrderCreate
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/m5-meal", tags=["A1-M5"])
service = MedicalService()


@router.get("/plans", response_model=ApiResponse)
def list_plans(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_meal_plans(db, current.tenant_id))


@router.post("/plans", response_model=ApiResponse)
def create_plan(payload: MealPlanCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_meal_plan(db, current.tenant_id, payload))


@router.get("/orders", response_model=ApiResponse)
def list_orders(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_meal_orders(db, current.tenant_id))


@router.post("/orders", response_model=ApiResponse)
def create_order(payload: MealOrderCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_meal_order(db, current.tenant_id, payload))
