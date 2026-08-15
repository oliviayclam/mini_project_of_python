import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import ROLE_ADMIN, ROLE_OPERATOR, get_current_user, require_roles
from app.models import FloorPlan, RouteSegment, User
from app.schemas import FloorPlanIn, FloorPlanOut, SegmentIn, SegmentOut
from app.services.audit import write_audit

router = APIRouter(tags=["floor-plans"])


def _length(seg: SegmentIn, scale: float) -> float:
    dx = seg.end_x - seg.start_x
    dy = seg.end_y - seg.start_y
    return round(math.sqrt(dx * dx + dy * dy) * scale, 3)


@router.get("/floors/{floor_id}/plan", response_model=FloorPlanOut)
def get_plan(floor_id: int, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    plan = (
        db.query(FloorPlan)
        .options(joinedload(FloorPlan.segments))
        .filter(FloorPlan.floor_id == floor_id)
        .first()
    )
    if not plan:
        plan = FloorPlan(floor_id=floor_id, canvas_data="{}")
        db.add(plan)
        db.commit()
        db.refresh(plan)
    return plan


@router.put("/floors/{floor_id}/plan", response_model=FloorPlanOut)
def put_plan(
    floor_id: int,
    payload: FloorPlanIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    plan = db.query(FloorPlan).filter(FloorPlan.floor_id == floor_id).first()
    if not plan:
        plan = FloorPlan(floor_id=floor_id)
        db.add(plan)
        db.flush()
    before = {"canvas_data": plan.canvas_data, "scale": plan.scale_m_per_px}
    plan.scale_m_per_px = payload.scale_m_per_px
    plan.canvas_data = payload.canvas_data
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="update",
        entity_type="floor_plan",
        entity_id=plan.id,
        before=before,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    plan = db.query(FloorPlan).options(joinedload(FloorPlan.segments)).get(plan.id)
    return plan


@router.post("/floors/{floor_id}/plan/segments", response_model=SegmentOut)
def add_segment(
    floor_id: int,
    payload: SegmentIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    plan = db.query(FloorPlan).filter(FloorPlan.floor_id == floor_id).first()
    if not plan:
        plan = FloorPlan(floor_id=floor_id)
        db.add(plan)
        db.flush()
    length = _length(payload, plan.scale_m_per_px)
    seg = RouteSegment(
        floor_plan_id=plan.id,
        start_x=payload.start_x,
        start_y=payload.start_y,
        end_x=payload.end_x,
        end_y=payload.end_y,
        path_length_m=length,
        notes=payload.notes,
    )
    db.add(seg)
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="route_segment",
        entity_id=None,
        after={**payload.model_dump(), "path_length_m": length},
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(seg)
    return seg


@router.post("/floors/{floor_id}/plan/estimate-path-length")
def estimate_length(
    floor_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    plan = (
        db.query(FloorPlan)
        .options(joinedload(FloorPlan.segments))
        .filter(FloorPlan.floor_id == floor_id)
        .first()
    )
    if not plan:
        raise HTTPException(404, "Floor plan not found")
    total = sum(s.path_length_m for s in plan.segments)
    return {"floor_id": floor_id, "estimated_length_m": round(total, 3), "segments": len(plan.segments)}
