import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models import AuditLog


def write_audit(
    db: Session,
    *,
    user_id: Optional[int],
    role: str,
    action: str,
    entity_type: str,
    entity_id: Any = None,
    before: Any = None,
    after: Any = None,
    request_path: str = "",
    ip_address: str = "",
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        role=role or "",
        action=action,
        entity_type=entity_type,
        entity_id=None if entity_id is None else str(entity_id),
        before_json="" if before is None else json.dumps(before, default=str),
        after_json="" if after is None else json.dumps(after, default=str),
        request_path=request_path,
        ip_address=ip_address,
    )
    db.add(log)
    db.flush()
    return log
