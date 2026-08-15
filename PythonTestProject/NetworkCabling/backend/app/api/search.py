from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Cable, CableType, Panel, Port, PortStatus, Rack, Room, Floor, ServiceType, User

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/assets")
def search_assets(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    cost_centre_id: Optional[int] = None,
    floor_id: Optional[int] = None,
    room_id: Optional[int] = None,
    rack_id: Optional[int] = None,
    panel_id: Optional[int] = None,
    port_remark: Optional[str] = None,
    cable_type_id: Optional[int] = None,
    service_type_id: Optional[int] = None,
    view_mode: str = "2d",
):
    racks_q = db.query(Rack)
    if cost_centre_id:
        racks_q = racks_q.filter(Rack.cost_centre_id == cost_centre_id)
    if floor_id:
        racks_q = racks_q.filter(Rack.floor_id == floor_id)
    if room_id:
        racks_q = racks_q.filter(Rack.room_id == room_id)
    if rack_id:
        racks_q = racks_q.filter(Rack.id == rack_id)
    racks = racks_q.all()

    panels_q = db.query(Panel)
    if rack_id:
        panels_q = panels_q.filter(Panel.rack_id == rack_id)
    if panel_id:
        panels_q = panels_q.filter(Panel.id == panel_id)
    if cost_centre_id:
        panels_q = panels_q.filter(Panel.cost_centre_id == cost_centre_id)
    panels = panels_q.all()

    ports_q = db.query(Port)
    if panel_id:
        ports_q = ports_q.filter(Port.panel_id == panel_id)
    elif panels:
        ports_q = ports_q.filter(Port.panel_id.in_([p.id for p in panels]))
    if port_remark:
        ports_q = ports_q.filter(Port.remark.ilike(f"%{port_remark}%"))
    ports = ports_q.all()

    cables_q = db.query(Cable)
    if cable_type_id:
        cables_q = cables_q.filter(Cable.cable_type_id == cable_type_id)
    if service_type_id:
        cables_q = cables_q.filter(Cable.service_type_id == service_type_id)
    cables = cables_q.all()

    statuses = {s.id: s for s in db.query(PortStatus).all()}
    cable_types = {c.id: c.name for c in db.query(CableType).all()}
    service_types = {s.id: s.name for s in db.query(ServiceType).all()}
    floors = {f.id: f.name for f in db.query(Floor).all()}
    rooms = {r.id: r.name for r in db.query(Room).all()}

    return {
        "view_mode": view_mode or "2d",
        "racks": [
            {
                "id": r.id,
                "name": r.name,
                "floor": floors.get(r.floor_id),
                "room": rooms.get(r.room_id),
                "manufacturer": r.manufacturer,
                "model": r.model,
                "u_height": r.u_height,
            }
            for r in racks
        ],
        "panels": [{"id": p.id, "name": p.name, "rack_id": p.rack_id, "port_count": p.port_count} for p in panels],
        "ports": [
            {
                "id": p.id,
                "name": p.name,
                "panel_id": p.panel_id,
                "remark": p.remark,
                "status": statuses[p.status_id].name if p.status_id in statuses else None,
                "color": statuses[p.status_id].color_hex if p.status_id in statuses else "#888",
            }
            for p in ports
        ],
        "cables": [
            {
                "id": c.id,
                "label": c.label,
                "cable_type": cable_types.get(c.cable_type_id),
                "service_type": service_types.get(c.service_type_id),
                "length_m": c.length_m,
                "a_port_id": c.a_port_id,
                "b_port_id": c.b_port_id,
                "b_customer_name": c.b_customer_name,
            }
            for c in cables
        ],
    }
