from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import ROLE_ADMIN, ROLE_OPERATOR, require_roles
from app.models import Panel, Port, PortStatus, Rack, Shelf, User
from app.schemas import AssetCreateIn, PanelOut, RackOut, ShelfOut
from app.services.audit import write_audit

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/odf-racks", response_model=RackOut)
def create_odf(
    payload: AssetCreateIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    rack = Rack(
        name=payload.name,
        cost_centre_id=payload.cost_centre_id,
        floor_id=payload.floor_id,
        room_id=payload.room_id,
        asset_type=payload.asset_type,
        rack_type=payload.rack_type,
        u_height=payload.shelf_or_u if payload.rack_type == "U" else 42,
        manufacturer=payload.manufacturer,
        model=payload.model,
        serial_number=payload.serial_number,
        install_date=payload.install_date,
        expire_date=payload.expire_date,
        asset_tag=payload.asset_tag,
        notes=payload.notes,
    )
    db.add(rack)
    db.flush()
    shelf = Shelf(
        rack_id=rack.id,
        name=f"{payload.name}-S1",
        u_position=payload.shelf_or_u,
        cost_centre_id=payload.cost_centre_id,
    )
    db.add(shelf)
    db.flush()
    panel = Panel(
        rack_id=rack.id,
        shelf_id=shelf.id,
        name=f"{payload.name}-P1",
        port_count=payload.port_count,
        u_position=payload.shelf_or_u,
        cost_centre_id=payload.cost_centre_id,
    )
    db.add(panel)
    db.flush()
    empty = db.query(PortStatus).filter(PortStatus.name.ilike("%empty%")).first()
    for i in range(1, payload.port_count + 1):
        db.add(
            Port(
                panel_id=panel.id,
                name=f"P{i:02d}",
                port_number=i,
                status_id=empty.id if empty else None,
            )
        )
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="odf_rack",
        entity_id=rack.id,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(rack)
    return rack


@router.post("/shelves", response_model=ShelfOut)
def create_shelf_asset(
    payload: AssetCreateIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    if not payload.rack_id:
        raise HTTPException(400, "rack_id required")
    shelf = Shelf(
        rack_id=payload.rack_id,
        name=payload.name,
        u_position=payload.shelf_or_u,
        cost_centre_id=payload.cost_centre_id,
    )
    db.add(shelf)
    db.flush()
    panel = Panel(
        rack_id=payload.rack_id,
        shelf_id=shelf.id,
        name=f"{payload.name}-P1",
        port_count=payload.port_count,
        u_position=payload.shelf_or_u,
        cost_centre_id=payload.cost_centre_id,
    )
    db.add(panel)
    db.flush()
    empty = db.query(PortStatus).filter(PortStatus.name.ilike("%empty%")).first()
    for i in range(1, payload.port_count + 1):
        db.add(Port(panel_id=panel.id, name=f"P{i:02d}", port_number=i, status_id=empty.id if empty else None))
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="shelf",
        entity_id=shelf.id,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(shelf)
    return shelf


@router.post("/panels", response_model=PanelOut)
def create_panel_asset(
    payload: AssetCreateIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    if not payload.rack_id:
        raise HTTPException(400, "rack_id required")
    panel = Panel(
        rack_id=payload.rack_id,
        name=payload.name,
        port_count=payload.port_count,
        u_position=payload.shelf_or_u,
        cost_centre_id=payload.cost_centre_id,
    )
    db.add(panel)
    db.flush()
    empty = db.query(PortStatus).filter(PortStatus.name.ilike("%empty%")).first()
    for i in range(1, payload.port_count + 1):
        db.add(Port(panel_id=panel.id, name=f"P{i:02d}", port_number=i, status_id=empty.id if empty else None))
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="panel",
        entity_id=panel.id,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(panel)
    return panel
