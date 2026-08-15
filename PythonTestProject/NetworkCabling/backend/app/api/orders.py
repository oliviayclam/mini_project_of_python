from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import (
    ROLE_ADMIN,
    ROLE_OPERATOR,
    ROLE_VENDOR,
    get_current_user,
    require_roles,
)
from app.models import CableOrder, CableOrderLine, CableType, RouteSegment, FloorPlan, ServiceType, User
from app.schemas import (
    CommentIn,
    OrderIn,
    OrderLineIn,
    OrderLineOut,
    OrderOut,
    SuggestionOut,
)
from app.services.audit import write_audit
from app.services.email import notify_workflow

router = APIRouter(prefix="/orders", tags=["orders"])


def _next_request_no(db: Session) -> str:
    count = db.query(CableOrder).count() + 1
    return f"WO-{1000 + count}"


def _order_out(order: CableOrder) -> OrderOut:
    return OrderOut(
        id=order.id,
        request_no=order.request_no,
        vendor_id=order.vendor_id,
        cost_centre_id=order.cost_centre_id,
        status=order.status,
        remarks=order.remarks,
        approver_comment=order.approver_comment,
        lines=[OrderLineOut.model_validate(l) for l in order.lines],
    )


@router.get("", response_model=list[OrderOut])
def list_orders(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    q = db.query(CableOrder).options(joinedload(CableOrder.lines))
    if user.role == ROLE_VENDOR:
        q = q.filter(CableOrder.vendor_id == user.id)
    orders = q.order_by(CableOrder.id.desc()).all()
    return [_order_out(o) for o in orders]


@router.post("", response_model=OrderOut)
def create_order(
    payload: OrderIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_VENDOR, ROLE_ADMIN))],
):
    vendor_id = user.id if user.role == ROLE_VENDOR else user.id
    order = CableOrder(
        request_no=_next_request_no(db),
        vendor_id=vendor_id,
        cost_centre_id=payload.cost_centre_id,
        status="draft",
        remarks=payload.remarks,
    )
    db.add(order)
    db.flush()
    for line in payload.lines:
        db.add(CableOrderLine(order_id=order.id, **line.model_dump()))
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="cable_order",
        entity_id=order.id,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    order = db.get(CableOrder, order.id)
    # reload lines
    order = db.query(CableOrder).options(joinedload(CableOrder.lines)).filter(CableOrder.id == order.id).one()
    return _order_out(order)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    order = db.query(CableOrder).options(joinedload(CableOrder.lines)).get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if user.role == ROLE_VENDOR and order.vendor_id != user.id:
        raise HTTPException(403, "Not your order")
    return _order_out(order)


@router.post("/{order_id}/lines", response_model=OrderLineOut)
def add_line(
    order_id: int,
    payload: OrderLineIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_VENDOR, ROLE_ADMIN))],
):
    order = db.get(CableOrder, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "draft":
        raise HTTPException(400, "Only draft orders can be edited")
    if user.role == ROLE_VENDOR and order.vendor_id != user.id:
        raise HTTPException(403, "Not your order")
    line = CableOrderLine(order_id=order.id, **payload.model_dump())
    db.add(line)
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="cable_order_line",
        entity_id=None,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(line)
    return line


@router.get("/{order_id}/suggestions", response_model=SuggestionOut)
def suggestions(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    order = db.query(CableOrder).options(joinedload(CableOrder.lines)).get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if user.role == ROLE_VENDOR and order.vendor_id != user.id:
        raise HTTPException(403, "Not your order")
    if order.status != "draft" and user.role == ROLE_VENDOR:
        # vendors get suggestions mainly for draft; operators can still view
        pass

    fiber = db.query(CableType).filter(CableType.category == "fiber").first()
    service = db.query(ServiceType).first()
    total_length = 0.0
    plan = db.query(FloorPlan).first()
    if plan:
        segs = db.query(RouteSegment).filter(RouteSegment.floor_plan_id == plan.id).all()
        total_length = sum(s.path_length_m for s in segs) or 15.0
    else:
        total_length = 15.0

    return SuggestionOut(
        cable_type_id=fiber.id if fiber else None,
        cable_type_name=fiber.name if fiber else None,
        service_type_id=service.id if service else None,
        service_type_name=service.name if service else None,
        estimated_length_m=round(total_length, 2),
        notes="Suggested from cable type master data and floor-plan route lengths",
    )


@router.post("/{order_id}/submit", response_model=OrderOut)
def submit_order(
    order_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_VENDOR, ROLE_ADMIN))],
):
    order = db.query(CableOrder).options(joinedload(CableOrder.lines)).get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "draft":
        raise HTTPException(400, "Only draft can be submitted")
    if user.role == ROLE_VENDOR and order.vendor_id != user.id:
        raise HTTPException(403, "Not your order")
    if not order.lines:
        raise HTTPException(400, "Add at least one full-path line")
    order.status = "submitted"
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="submit",
        entity_type="cable_order",
        entity_id=order.id,
        after={"status": "submitted"},
        request_path=str(request.url.path),
    )
    ops = db.query(User).filter(User.role.in_([ROLE_OPERATOR, ROLE_ADMIN])).all()
    for op in ops:
        notify_workflow(
            db,
            event="pending",
            to_address=op.email,
            entity_label="CableOrder",
            request_no=order.request_no,
            detail="Awaiting approval",
            user_id=user.id,
            role=user.role,
        )
    notify_workflow(
        db,
        event="submit",
        to_address=user.email,
        entity_label="CableOrder",
        request_no=order.request_no,
        detail="Your request was submitted",
        user_id=user.id,
        role=user.role,
    )
    db.commit()
    return _order_out(order)


@router.post("/{order_id}/approve", response_model=OrderOut)
def approve_order(
    order_id: int,
    payload: CommentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))],
):
    order = db.query(CableOrder).options(joinedload(CableOrder.lines)).get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "submitted":
        raise HTTPException(400, "Order is not pending approval")
    order.status = "approved"
    order.approver_comment = payload.comment
    order.approved_by = user.id
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="approve",
        entity_type="cable_order",
        entity_id=order.id,
        after={"status": "approved", "comment": payload.comment},
        request_path=str(request.url.path),
    )
    vendor = db.get(User, order.vendor_id)
    if vendor:
        notify_workflow(
            db,
            event="approve",
            to_address=vendor.email,
            entity_label="CableOrder",
            request_no=order.request_no,
            detail=payload.comment,
            user_id=user.id,
            role=user.role,
        )
    db.commit()
    return _order_out(order)


@router.post("/{order_id}/reject", response_model=OrderOut)
def reject_order(
    order_id: int,
    payload: CommentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))],
):
    order = db.query(CableOrder).options(joinedload(CableOrder.lines)).get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "submitted":
        raise HTTPException(400, "Order is not pending approval")
    order.status = "rejected"
    order.approver_comment = payload.comment
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="reject",
        entity_type="cable_order",
        entity_id=order.id,
        after={"status": "rejected", "comment": payload.comment},
        request_path=str(request.url.path),
    )
    vendor = db.get(User, order.vendor_id)
    if vendor:
        notify_workflow(
            db,
            event="reject",
            to_address=vendor.email,
            entity_label="CableOrder",
            request_no=order.request_no,
            detail=payload.comment,
            user_id=user.id,
            role=user.role,
        )
    db.commit()
    return _order_out(order)
