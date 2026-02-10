from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.oa import NotificationMessageCreate
from app.services.oa_service import OAService

router = APIRouter(prefix="/oa3-notification", tags=["A2-OA3"])
service = OAService()


@router.get("/messages", response_model=ApiResponse)
def list_messages(db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_notifications(db, current.tenant_id))


@router.post("/messages", response_model=ApiResponse)
def create_message(payload: NotificationMessageCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(message="created", data=service.create_notification(db, current.tenant_id, payload))
