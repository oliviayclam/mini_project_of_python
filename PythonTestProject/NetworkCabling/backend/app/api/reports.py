from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    ROLE_ADMIN,
    ROLE_DEPT_ADMIN,
    ROLE_OPERATOR,
    get_current_user,
    require_roles,
)
from app.models import (
    Cable,
    CableOrder,
    Panel,
    Port,
    PortStatus,
    TerminationRequest,
    User,
)
from app.schemas import CommentIn, TerminationIn, TerminationOut
from app.services.audit import write_audit
from app.services.email import notify_workflow

router = APIRouter(tags=["admin-reports"])


def _term_no(db: Session) -> str:
    return f"TR-{1000 + db.query(TerminationRequest).count() + 1}"


@router.get("/termination-requests", response_model=list[TerminationOut])
def list_terms(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(TerminationRequest).order_by(TerminationRequest.id.desc()).all()


@router.post("/termination-requests", response_model=TerminationOut)
def create_term(
    payload: TerminationIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    row = TerminationRequest(
        request_no=_term_no(db),
        requester_id=user.id,
        cable_id=payload.cable_id,
        order_id=payload.order_id,
        reason=payload.reason,
        status="submitted",
    )
    db.add(row)
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="termination_request",
        entity_id=None,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    for op in db.query(User).filter(User.role.in_([ROLE_OPERATOR, ROLE_ADMIN])).all():
        notify_workflow(
            db,
            event="pending",
            to_address=op.email,
            entity_label="TerminationRequest",
            request_no=row.request_no,
            detail=payload.reason,
            user_id=user.id,
            role=user.role,
        )
    db.commit()
    db.refresh(row)
    return row


@router.post("/termination-requests/{term_id}/approve", response_model=TerminationOut)
def approve_term(
    term_id: int,
    payload: CommentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))],
):
    row = db.get(TerminationRequest, term_id)
    if not row:
        raise HTTPException(404, "Not found")
    row.status = "approved"
    row.approver_comment = payload.comment
    if row.cable_id:
        cable = db.get(Cable, row.cable_id)
        if cable:
            cable.status = "terminated"
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="approve",
        entity_type="termination_request",
        entity_id=row.id,
        after={"status": "approved"},
        request_path=str(request.url.path),
    )
    requester = db.get(User, row.requester_id)
    if requester:
        notify_workflow(
            db,
            event="approve",
            to_address=requester.email,
            entity_label="TerminationRequest",
            request_no=row.request_no,
            detail=payload.comment,
            user_id=user.id,
            role=user.role,
        )
    db.commit()
    db.refresh(row)
    return row


@router.post("/termination-requests/{term_id}/reject", response_model=TerminationOut)
def reject_term(
    term_id: int,
    payload: CommentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))],
):
    row = db.get(TerminationRequest, term_id)
    if not row:
        raise HTTPException(404, "Not found")
    row.status = "rejected"
    row.approver_comment = payload.comment
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="reject",
        entity_type="termination_request",
        entity_id=row.id,
        after={"status": "rejected"},
        request_path=str(request.url.path),
    )
    requester = db.get(User, row.requester_id)
    if requester:
        notify_workflow(
            db,
            event="reject",
            to_address=requester.email,
            entity_label="TerminationRequest",
            request_no=row.request_no,
            detail=payload.comment,
            user_id=user.id,
            role=user.role,
        )
    db.commit()
    db.refresh(row)
    return row


@router.get("/reports/invoice")
def invoice_report(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_DEPT_ADMIN))],
):
    orders = db.query(CableOrder).filter(CableOrder.status == "approved").all()
    return {
        "report": "invoice",
        "rows": [
            {
                "request_no": o.request_no,
                "cost_centre_id": o.cost_centre_id,
                "vendor_id": o.vendor_id,
                "status": o.status,
            }
            for o in orders
        ],
    }


@router.get("/reports/inspection")
def inspection_report(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    fail = db.query(PortStatus).filter(PortStatus.name.ilike("%fail%")).first()
    ports = db.query(Port).filter(Port.status_id == fail.id).all() if fail else []
    return {"report": "inspection", "fail_ports": [{"id": p.id, "name": p.name, "remark": p.remark} for p in ports]}


@router.get("/reports/termination")
def termination_report(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    rows = db.query(TerminationRequest).all()
    return {
        "report": "termination",
        "rows": [{"request_no": r.request_no, "status": r.status, "reason": r.reason} for r in rows],
    }


@router.get("/reports/cabling-mark-area")
def mark_area_report(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    cables = db.query(Cable).all()
    return {
        "report": "cabling_mark_area",
        "rows": [{"id": c.id, "label": c.label, "notes": c.notes, "length_m": c.length_m} for c in cables],
    }


@router.get("/reports/exception")
def exception_report(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    reserved = db.query(PortStatus).filter(PortStatus.name.ilike("%reserved%")).first()
    ports = db.query(Port).filter(Port.status_id == reserved.id).all() if reserved else []
    return {
        "report": "exception",
        "reserved_ports": [{"id": p.id, "name": p.name, "remark": p.remark} for p in ports],
    }


@router.get("/reports/structured-cable")
def structured_cable_report(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    cables = db.query(Cable).all()
    return {
        "report": "structured_cable",
        "rows": [
            {
                "id": c.id,
                "label": c.label,
                "a_port_id": c.a_port_id,
                "b_port_id": c.b_port_id,
                "b_customer_name": c.b_customer_name,
                "length_m": c.length_m,
            }
            for c in cables
        ],
    }


@router.get("/reports/odf-patch-utilization")
def utilization_report(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    panels = db.query(Panel).all()
    empty = db.query(PortStatus).filter(PortStatus.name.ilike("%empty%")).first()
    result = []
    for panel in panels:
        ports = db.query(Port).filter(Port.panel_id == panel.id).all()
        empty_count = sum(1 for p in ports if empty and p.status_id == empty.id)
        result.append(
            {
                "panel_id": panel.id,
                "panel": panel.name,
                "total_ports": len(ports),
                "empty_ports": empty_count,
                "used_ports": len(ports) - empty_count,
                "utilization_pct": round(((len(ports) - empty_count) / len(ports) * 100) if ports else 0, 1),
            }
        )
    return {"report": "odf_patch_utilization", "rows": result}


@router.get("/dashboard")
def dashboard(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    empty = db.query(PortStatus).filter(PortStatus.name.ilike("%empty%")).first()
    free_ports = db.query(Port).filter(Port.status_id == empty.id).count() if empty else 0
    return {
        "free_ports": free_ports,
        "pending_orders": db.query(CableOrder).filter(CableOrder.status == "submitted").count(),
        "approved_orders": db.query(CableOrder).filter(CableOrder.status == "approved").count(),
        "cables": db.query(Cable).count(),
        "panels": db.query(Panel).count(),
    }
