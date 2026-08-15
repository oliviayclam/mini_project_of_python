from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import ROLE_ADMIN, ROLE_OPERATOR, get_current_user, require_roles
from app.models import (
    Cable,
    CableType,
    CostCentre,
    Device,
    Floor,
    Panel,
    Port,
    PortStatus,
    Rack,
    Room,
    ServiceType,
    Shelf,
    Site,
    Cage,
    User,
)
from app.schemas import (
    CableIn,
    CableOut,
    CableTypeIn,
    CableTypeOut,
    CostCentreIn,
    CostCentreOut,
    DeviceIn,
    DeviceOut,
    FloorIn,
    FloorOut,
    PanelIn,
    PanelOut,
    PortOut,
    PortRemarkIn,
    PortStatusIn,
    PortStatusOut,
    PortStatusUpdateIn,
    RackIn,
    RackOut,
    CageIn,
    CageOut,
    RoomIn,
    RoomOut,
    ServiceTypeIn,
    ServiceTypeOut,
    ShelfIn,
    ShelfOut,
    SiteIn,
    SiteOut,
)
from app.services.audit import write_audit

router = APIRouter(tags=["inventory"])


def _audit(db, request: Request, user: User, action: str, entity_type: str, entity_id, before=None, after=None):
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        request_path=str(request.url.path),
        ip_address=request.client.host if request.client else "",
    )


@router.get("/sites", response_model=list[SiteOut])
def list_sites(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Site).all()


@router.post("/sites", response_model=SiteOut)
def create_site(
    payload: SiteIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = Site(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "site", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/floors", response_model=list[FloorOut])
def list_floors(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Floor).all()


@router.post("/floors", response_model=FloorOut)
def create_floor(
    payload: FloorIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = Floor(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "floor", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/rooms", response_model=list[RoomOut])
def list_rooms(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Room).all()


@router.post("/rooms", response_model=RoomOut)
def create_room(
    payload: RoomIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = Room(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "room", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/cost-centres", response_model=list[CostCentreOut])
def list_cc(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(CostCentre).all()


@router.post("/cost-centres", response_model=CostCentreOut)
def create_cc(
    payload: CostCentreIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
):
    row = CostCentre(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "cost_centre", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/cable-types", response_model=list[CableTypeOut])
def list_cable_types(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(CableType).all()


@router.post("/cable-types", response_model=CableTypeOut)
def create_cable_type(
    payload: CableTypeIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
):
    row = CableType(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "cable_type", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/service-types", response_model=list[ServiceTypeOut])
def list_service_types(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(ServiceType).all()


@router.post("/service-types", response_model=ServiceTypeOut)
def create_service_type(
    payload: ServiceTypeIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
):
    row = ServiceType(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "service_type", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/port-statuses", response_model=list[PortStatusOut])
def list_port_statuses(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(PortStatus).all()


@router.post("/port-statuses", response_model=PortStatusOut)
def create_port_status(
    payload: PortStatusIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
):
    row = PortStatus(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "port_status", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.patch("/port-statuses/{status_id}", response_model=PortStatusOut)
def update_port_status_color(
    status_id: int,
    payload: PortStatusIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
):
    row = db.get(PortStatus, status_id)
    if not row:
        raise HTTPException(404, "Port status not found")
    before = {"name": row.name, "color_hex": row.color_hex}
    row.name = payload.name
    row.color_hex = payload.color_hex
    row.is_system_status = payload.is_system_status
    _audit(db, request, user, "update", "port_status", row.id, before=before, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/racks", response_model=list[RackOut])
def list_racks(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Rack).all()


@router.get("/racks/{rack_id}", response_model=RackOut)
def get_rack(rack_id: int, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    row = db.get(Rack, rack_id)
    if not row:
        raise HTTPException(404, "Rack not found")
    return row


@router.post("/racks", response_model=RackOut)
def create_rack(
    payload: RackIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = Rack(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "rack", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/cages", response_model=list[CageOut])
def list_cages(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Cage).all()


@router.post("/cages", response_model=CageOut)
def create_cage(
    payload: CageIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = Cage(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "cage", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/shelves", response_model=list[ShelfOut])
def list_shelves(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Shelf).all()


@router.post("/shelves", response_model=ShelfOut)
def create_shelf(
    payload: ShelfIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = Shelf(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "shelf", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/panels", response_model=list[PanelOut])
def list_panels(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Panel).all()


@router.post("/panels", response_model=PanelOut)
def create_panel(
    payload: PanelIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    data = payload.model_dump()
    create_ports = data.pop("create_ports", True)
    row = Panel(**data)
    db.add(row)
    db.flush()
    if create_ports:
        empty = db.query(PortStatus).filter(PortStatus.name.ilike("%empty%")).first()
        for i in range(1, row.port_count + 1):
            db.add(
                Port(
                    panel_id=row.id,
                    name=f"P{i:02d}",
                    port_number=i,
                    status_id=empty.id if empty else None,
                )
            )
    _audit(db, request, user, "create", "panel", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/devices", response_model=list[DeviceOut])
def list_devices(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Device).all()


@router.post("/devices", response_model=DeviceOut)
def create_device(
    payload: DeviceIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = Device(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "device", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/ports", response_model=list[PortOut])
def list_ports(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    panel_id: Optional[int] = None,
    rack_id: Optional[int] = None,
):
    q = db.query(Port)
    if panel_id:
        q = q.filter(Port.panel_id == panel_id)
    if rack_id:
        panel_ids = [p.id for p in db.query(Panel).filter(Panel.rack_id == rack_id).all()]
        q = q.filter(Port.panel_id.in_(panel_ids))
    return q.all()


@router.patch("/ports/{port_id}/remark", response_model=PortOut)
def update_remark(
    port_id: int,
    payload: PortRemarkIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = db.get(Port, port_id)
    if not row:
        raise HTTPException(404, "Port not found")
    before = {"remark": row.remark}
    row.remark = payload.remark
    _audit(db, request, user, "update", "port", row.id, before=before, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.patch("/ports/{port_id}/status", response_model=PortOut)
def update_port_status(
    port_id: int,
    payload: PortStatusUpdateIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = db.get(Port, port_id)
    if not row:
        raise HTTPException(404, "Port not found")
    if not db.get(PortStatus, payload.status_id):
        raise HTTPException(404, "Status not found")
    before = {"status_id": row.status_id}
    row.status_id = payload.status_id
    _audit(db, request, user, "update", "port", row.id, before=before, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row


@router.get("/cables", response_model=list[CableOut])
def list_cables(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Cable).all()


@router.post("/cables", response_model=CableOut)
@router.post("/structured-cables", response_model=CableOut)
def create_cable(
    payload: CableIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN, ROLE_OPERATOR))],
):
    row = Cable(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, request, user, "create", "cable", row.id, after=payload.model_dump())
    db.commit()
    db.refresh(row)
    return row
