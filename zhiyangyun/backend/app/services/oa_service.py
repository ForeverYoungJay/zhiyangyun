from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.oa import (
    ShiftTemplate,
    ShiftAssignment,
    ApprovalRequest,
    NotificationMessage,
    TrainingCourse,
    TrainingRecord,
)
from app.schemas.oa import (
    ShiftTemplateCreate,
    ShiftAssignmentCreate,
    ApprovalRequestCreate,
    NotificationMessageCreate,
    TrainingCourseCreate,
    TrainingRecordCreate,
)


class OAService:
    def _save(self, db: Session, obj):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_shifts(self, db: Session, tenant_id: str):
        return db.scalars(select(ShiftTemplate).where(ShiftTemplate.tenant_id == tenant_id)).all()

    def create_shift(self, db: Session, tenant_id: str, payload: ShiftTemplateCreate):
        return self._save(db, ShiftTemplate(tenant_id=tenant_id, **payload.model_dump()))

    def list_assignments(self, db: Session, tenant_id: str):
        return db.scalars(select(ShiftAssignment).where(ShiftAssignment.tenant_id == tenant_id)).all()

    def create_assignment(self, db: Session, tenant_id: str, payload: ShiftAssignmentCreate):
        return self._save(db, ShiftAssignment(tenant_id=tenant_id, **payload.model_dump()))

    def list_approvals(self, db: Session, tenant_id: str):
        return db.scalars(select(ApprovalRequest).where(ApprovalRequest.tenant_id == tenant_id)).all()

    def create_approval(self, db: Session, tenant_id: str, payload: ApprovalRequestCreate):
        return self._save(db, ApprovalRequest(tenant_id=tenant_id, **payload.model_dump()))

    def list_notifications(self, db: Session, tenant_id: str):
        return db.scalars(select(NotificationMessage).where(NotificationMessage.tenant_id == tenant_id)).all()

    def create_notification(self, db: Session, tenant_id: str, payload: NotificationMessageCreate):
        return self._save(db, NotificationMessage(tenant_id=tenant_id, **payload.model_dump()))

    def list_courses(self, db: Session, tenant_id: str):
        return db.scalars(select(TrainingCourse).where(TrainingCourse.tenant_id == tenant_id)).all()

    def create_course(self, db: Session, tenant_id: str, payload: TrainingCourseCreate):
        return self._save(db, TrainingCourse(tenant_id=tenant_id, **payload.model_dump()))

    def list_records(self, db: Session, tenant_id: str):
        return db.scalars(select(TrainingRecord).where(TrainingRecord.tenant_id == tenant_id)).all()

    def create_record(self, db: Session, tenant_id: str, payload: TrainingRecordCreate):
        return self._save(db, TrainingRecord(tenant_id=tenant_id, **payload.model_dump()))
