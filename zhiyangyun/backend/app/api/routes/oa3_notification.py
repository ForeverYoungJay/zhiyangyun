from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.oa import NotificationActionPayload, NotificationMessageCreate
from app.services.oa_service import OAService

router = APIRouter(prefix="/oa3-notification", tags=["A2-OA3"])
service = OAService()


@router.get("/users/suggest", response_model=ApiResponse)
def suggest_users(keyword: str = "", limit: int = 20, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.suggest_users(db, current.tenant_id, keyword=keyword, limit=limit))


@router.get("/messages", response_model=ApiResponse)
def list_messages(page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", channel: str = "", strategy: str = "", receiver_scope: str = "", db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    return ApiResponse(data=service.list_notifications(db, current.tenant_id, page=page, page_size=page_size, keyword=keyword, status=status, channel=channel, strategy=strategy, receiver_scope=receiver_scope))


@router.post("/messages", response_model=ApiResponse)
def create_message(payload: NotificationMessageCreate, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="created", data=service.create_notification(db, current.tenant_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/messages/{message_id}/action", response_model=ApiResponse)
def action_message(message_id: str, payload: NotificationActionPayload, db: Session = Depends(get_db), current: CurrentUser = Depends(get_current_user)):
    try:
        return ApiResponse(message="updated", data=service.action_notification(db, current.tenant_id, message_id, payload))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
