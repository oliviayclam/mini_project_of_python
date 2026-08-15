from datetime import date

from sqlalchemy.orm import Session

from app.core.security import (
    ROLE_ADMIN,
    ROLE_DEPT_ADMIN,
    ROLE_OPERATOR,
    ROLE_VENDOR,
    hash_password,
)
from app.models import (
    Cable,
    CableOrder,
    CableOrderLine,
    CableType,
    CostCentre,
    Device,
    DwdmLink,
    DwdmSystem,
    Floor,
    FloorPlan,
    OpticalChannel,
    Panel,
    Port,
    PortStatus,
    Rack,
    Room,
    ServiceType,
    Shelf,
    Site,
    User,
)


def seed_database(db: Session) -> None:
    if db.query(User).first():
        return

    users = [
        User(
            username="admin",
            email="admin@example.com",
            full_name="System Admin",
            hashed_password=hash_password("admin123"),
            role=ROLE_ADMIN,
        ),
        User(
            username="operator",
            email="operator@example.com",
            full_name="Ops Operator",
            hashed_password=hash_password("operator123"),
            role=ROLE_OPERATOR,
        ),
        User(
            username="operator2",
            email="operator2@example.com",
            full_name="Second Approver",
            hashed_password=hash_password("operator123"),
            role=ROLE_OPERATOR,
        ),
        User(
            username="vendor",
            email="vendor@example.com",
            full_name="Cable Vendor",
            hashed_password=hash_password("vendor123"),
            role=ROLE_VENDOR,
        ),
        User(
            username="deptadmin",
            email="deptadmin@example.com",
            full_name="Department Admin",
            hashed_password=hash_password("dept123"),
            role=ROLE_DEPT_ADMIN,
        ),
    ]
    db.add_all(users)
    db.flush()

    cc = CostCentre(code="CC-100", name="Data Centre Ops", address="1 Network Rd", owner="IT")
    db.add(cc)
    db.flush()

    site = Site(name="HKDC1", code="HKDC1", address="Hong Kong Data Centre 1")
    db.add(site)
    db.flush()

    floor = Floor(site_id=site.id, name="Floor 3", level_no=3, ownership="own")
    db.add(floor)
    db.flush()

    room = Room(floor_id=floor.id, name="MMR-A", is_rental=False)
    db.add(room)
    db.flush()

    statuses = [
        PortStatus(name="Empty Port in the Panel", color_hex="#94a3b8", is_system_status=True),
        PortStatus(name="Port Reserved by draft", color_hex="#f59e0b", is_system_status=True),
        PortStatus(name="Fail Port", color_hex="#ef4444", is_system_status=True),
        PortStatus(name="New Port in the Panel", color_hex="#22c55e", is_system_status=True),
        PortStatus(name="In Use", color_hex="#3b82f6", is_system_status=True),
    ]
    db.add_all(statuses)
    db.flush()

    ct_fiber = CableType(
        name="OS2 Singlemode",
        category="fiber",
        connector_a="LC",
        connector_b="LC",
        default_color="#fbbf24",
        supported_lengths="5,10,15,20,30,50",
    )
    ct_copper = CableType(
        name="Cat6",
        category="copper",
        connector_a="RJ45",
        connector_b="RJ45",
        default_color="#2563eb",
        supported_lengths="1,2,3,5,10",
    )
    db.add_all([ct_fiber, ct_copper])

    st_dia = ServiceType(name="DIA", service_category="Internet", bandwidth_profile="1G")
    st_p2p = ServiceType(name="P2P", service_category="Private", bandwidth_profile="10G")
    db.add_all([st_dia, st_p2p])
    db.flush()

    rack = Rack(
        name="ODF-R01",
        cost_centre_id=cc.id,
        floor_id=floor.id,
        room_id=room.id,
        asset_type="ODF",
        rack_type="Shelf",
        u_height=42,
        manufacturer="Panduit",
        model="ODF-42U",
        serial_number="SN-ODF-001",
        install_date=date(2024, 1, 15),
        expire_date=date(2029, 1, 15),
        asset_tag="AT-RACK-001",
        power_feed="A+B",
        notes="Main MMR ODF",
    )
    db.add(rack)
    db.flush()

    shelf = Shelf(rack_id=rack.id, name="Shelf-1", u_position=40, cost_centre_id=cc.id)
    db.add(shelf)
    db.flush()

    panel = Panel(
        shelf_id=shelf.id,
        rack_id=rack.id,
        name="PP-01",
        port_count=24,
        u_position=40,
        cost_centre_id=cc.id,
    )
    db.add(panel)
    db.flush()

    device = Device(
        rack_id=rack.id,
        name="SW-CORE-01",
        device_type="switch",
        u_start=1,
        u_height=2,
        manufacturer="Cisco",
        model="N9K",
    )
    db.add(device)
    db.flush()

    ports = []
    empty = statuses[0]
    in_use = statuses[4]
    for i in range(1, 25):
        p = Port(
            panel_id=panel.id,
            name=f"P{i:02d}",
            port_number=i,
            connector_type="LC",
            status_id=in_use.id if i <= 2 else empty.id,
            remark="Seed port" if i <= 2 else "",
        )
        ports.append(p)
    db.add_all(ports)
    db.flush()

    cable = Cable(
        cable_type_id=ct_fiber.id,
        service_type_id=st_dia.id,
        length_m=15.0,
        color="#fbbf24",
        status="active",
        a_port_id=ports[0].id,
        b_customer_name="Customer A",
        label="CBL-0001",
    )
    db.add(cable)

    vendor = next(u for u in users if u.role == ROLE_VENDOR)
    order = CableOrder(
        request_no="WO-1001",
        vendor_id=vendor.id,
        cost_centre_id=cc.id,
        status="submitted",
        remarks="New customer patch",
    )
    db.add(order)
    db.flush()
    db.add(
        CableOrderLine(
            order_id=order.id,
            line_no=1,
            cable_type_id=ct_fiber.id,
            service_type_id=st_dia.id,
            path_group="A",
            path_index=1,
            endpoint_a="PP-01 / P03",
            endpoint_b="Customer A Cage",
            a_port_id=ports[2].id,
            requested_length_m=20,
            routing_notes="Via tray T1",
        )
    )

    plan = FloorPlan(floor_id=floor.id, scale_m_per_px=0.05, canvas_data='{"rooms":[]}')
    db.add(plan)

    dsys = DwdmSystem(name="Ring-East", description="Optional DWDM extension sample")
    db.add(dsys)
    db.flush()
    dlink = DwdmLink(
        system_id=dsys.id,
        name="HKDC1-HKDC2",
        site_a_id=site.id,
        distance_km=12.5,
        fiber_path="Dark fiber pair 1",
    )
    db.add(dlink)
    db.flush()
    db.add(
        OpticalChannel(
            link_id=dlink.id,
            itu_channel="C21",
            wavelength_nm=1560.61,
            direction="bi",
            client_service="10G DIA",
            status="up",
            port_id=ports[0].id,
        )
    )

    db.commit()
