import csv
import io
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import ROLE_ADMIN, require_roles
from app.models import AuditLog, User
from app.schemas import AuditOut
from app.services.audit import write_audit

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditOut])
def list_logs(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    q = db.query(AuditLog)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if date_from:
        q = q.filter(AuditLog.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        q = q.filter(AuditLog.created_at <= datetime.fromisoformat(date_to))
    return q.order_by(AuditLog.id.desc()).limit(500).all()


@router.get("/export")
def export_logs(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
    format: str = "csv",
):
    rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(2000).all()
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="export",
        entity_type="audit_log",
        entity_id=None,
        after={"count": len(rows), "format": format},
        request_path=str(request.url.path),
    )
    db.commit()

    if format == "json":
        import json

        data = [
            {
                "id": r.id,
                "user_id": r.user_id,
                "role": r.role,
                "action": r.action,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "created_at": str(r.created_at),
            }
            for r in rows
        ]
        return Response(content=json.dumps(data, indent=2), media_type="application/json")

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "user_id", "role", "action", "entity_type", "entity_id", "created_at", "request_path"])
    for r in rows:
        writer.writerow([r.id, r.user_id, r.role, r.action, r.entity_type, r.entity_id, r.created_at, r.request_path])
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )
