import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import ROLE_ADMIN, ROLE_OPERATOR, get_current_user, require_roles
from app.models import ChangeRequest, ChangeRequestApproval, Port, Rack, User
from app.schemas import ChangeRequestIn, ChangeRequestOut, CommentIn
from app.services.audit import write_audit
from app.services.email import notify_workflow

router = APIRouter(prefix="/change-requests", tags=["change-requests"])


def _next_no(db: Session) -> str:
    return f"CR-{1000 + db.query(ChangeRequest).count() + 1}"


def _out(row: ChangeRequest) -> ChangeRequestOut:
    return ChangeRequestOut.model_validate(row)


@router.get("", response_model=list[ChangeRequestOut])
def list_crs(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    q = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals))
    if user.role not in (ROLE_ADMIN, ROLE_OPERATOR):
        q = q.filter(ChangeRequest.requester_id == user.id)
    return q.order_by(ChangeRequest.id.desc()).all()


@router.post("", response_model=ChangeRequestOut)
def create_cr(
    payload: ChangeRequestIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    required = payload.required_approvals
    if payload.change_type in ("replace", "install_new") and required < 1:
        required = 2
    required = max(1, min(2, required))
    row = ChangeRequest(
        request_no=_next_no(db),
        requester_id=user.id,
        change_type=payload.change_type,
        target_entity_type=payload.target_entity_type,
        target_entity_id=payload.target_entity_id,
        proposed_changes_json=json.dumps(payload.proposed_changes),
        status="draft",
        required_approvals=required,
    )
    db.add(row)
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="change_request",
        entity_id=None,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(row)
    return _out(row)


@router.get("/{cr_id}", response_model=ChangeRequestOut)
def get_cr(cr_id: int, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    row = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals)).get(cr_id)
    if not row:
        raise HTTPException(404, "Not found")
    return _out(row)


@router.post("/{cr_id}/submit", response_model=ChangeRequestOut)
def submit_cr(
    cr_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    row = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals)).get(cr_id)
    if not row:
        raise HTTPException(404, "Not found")
    if row.requester_id != user.id and user.role != ROLE_ADMIN:
        raise HTTPException(403, "Not allowed")
    if row.status != "draft":
        raise HTTPException(400, "Only draft can submit")
    row.status = "submitted"
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="submit",
        entity_type="change_request",
        entity_id=row.id,
        after={"status": "submitted"},
        request_path=str(request.url.path),
    )
    for op in db.query(User).filter(User.role.in_([ROLE_OPERATOR, ROLE_ADMIN])).all():
        notify_workflow(
            db,
            event="pending",
            to_address=op.email,
            entity_label="ChangeRequest",
            request_no=row.request_no,
            detail=f"Type={row.change_type}",
            user_id=user.id,
            role=user.role,
        )
    db.commit()
    return _out(row)


@router.post("/{cr_id}/approve", response_model=ChangeRequestOut)
def approve_cr(
    cr_id: int,
    payload: CommentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))],
):
    row = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals)).get(cr_id)
    if not row:
        raise HTTPException(404, "Not found")
    if row.status not in ("submitted", "pending_second"):
        raise HTTPException(400, "Not awaiting approval")
    if any(a.approver_id == user.id and a.decision == "approve" for a in row.approvals):
        raise HTTPException(400, "You already approved")

    db.add(
        ChangeRequestApproval(
            change_request_id=row.id,
            approver_id=user.id,
            decision="approve",
            comment=payload.comment,
        )
    )
    db.flush()
    db.refresh(row)
    approvals = [a for a in row.approvals if a.decision == "approve"]
    if len(approvals) >= row.required_approvals:
        row.status = "approved"
        requester = db.get(User, row.requester_id)
        if requester:
            notify_workflow(
                db,
                event="approve",
                to_address=requester.email,
                entity_label="ChangeRequest",
                request_no=row.request_no,
                detail=payload.comment,
                user_id=user.id,
                role=user.role,
            )
    else:
        row.status = "pending_second"
        for op in db.query(User).filter(User.role.in_([ROLE_OPERATOR, ROLE_ADMIN]), User.id != user.id).all():
            notify_workflow(
                db,
                event="pending",
                to_address=op.email,
                entity_label="ChangeRequest",
                request_no=row.request_no,
                detail="Second approval required",
                user_id=user.id,
                role=user.role,
            )

    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="approve",
        entity_type="change_request",
        entity_id=row.id,
        after={"status": row.status, "comment": payload.comment},
        request_path=str(request.url.path),
    )
    db.commit()
    row = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals)).get(cr_id)
    return _out(row)


@router.post("/{cr_id}/reject", response_model=ChangeRequestOut)
def reject_cr(
    cr_id: int,
    payload: CommentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))],
):
    row = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals)).get(cr_id)
    if not row:
        raise HTTPException(404, "Not found")
    row.status = "rejected"
    db.add(
        ChangeRequestApproval(
            change_request_id=row.id,
            approver_id=user.id,
            decision="reject",
            comment=payload.comment,
        )
    )
    requester = db.get(User, row.requester_id)
    if requester:
        notify_workflow(
            db,
            event="reject",
            to_address=requester.email,
            entity_label="ChangeRequest",
            request_no=row.request_no,
            detail=payload.comment,
            user_id=user.id,
            role=user.role,
        )
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="reject",
        entity_type="change_request",
        entity_id=row.id,
        after={"status": "rejected", "comment": payload.comment},
        request_path=str(request.url.path),
    )
    db.commit()
    row = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals)).get(cr_id)
    return _out(row)


@router.post("/{cr_id}/apply", response_model=ChangeRequestOut)
def apply_cr(
    cr_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    row = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals)).get(cr_id)
    if not row:
        raise HTTPException(404, "Not found")
    if row.status != "approved":
        raise HTTPException(400, "Change request must be approved before apply")
    if row.applied:
        raise HTTPException(400, "Already applied")
    if row.requester_id != user.id and user.role != ROLE_ADMIN:
        raise HTTPException(403, "Only requester or admin can apply")

    changes = json.loads(row.proposed_changes_json or "{}")
    before = {}
    after = {}
    if row.target_entity_type == "rack" and row.target_entity_id:
        rack = db.get(Rack, row.target_entity_id)
        if not rack:
            raise HTTPException(404, "Rack not found")
        before = {k: getattr(rack, k, None) for k in changes}
        for k, v in changes.items():
            if hasattr(rack, k):
                setattr(rack, k, v)
        after = {k: getattr(rack, k, None) for k in changes}
    elif row.target_entity_type == "port" and row.target_entity_id:
        port = db.get(Port, row.target_entity_id)
        if not port:
            raise HTTPException(404, "Port not found")
        before = {k: getattr(port, k, None) for k in changes}
        for k, v in changes.items():
            if hasattr(port, k):
                setattr(port, k, v)
        after = {k: getattr(port, k, None) for k in changes}
    elif row.change_type == "install_new" and row.target_entity_type == "rack":
        rack = Rack(name=changes.get("name", "New Rack"), **{k: v for k, v in changes.items() if k != "name" and hasattr(Rack, k)})
        db.add(rack)
        db.flush()
        after = {"id": rack.id, **changes}

    row.applied = True
    row.status = "applied"
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="update",
        entity_type=row.target_entity_type,
        entity_id=row.target_entity_id,
        before=before,
        after=after,
        request_path=str(request.url.path),
    )
    db.commit()
    row = db.query(ChangeRequest).options(joinedload(ChangeRequest.approvals)).get(cr_id)
    return _out(row)
