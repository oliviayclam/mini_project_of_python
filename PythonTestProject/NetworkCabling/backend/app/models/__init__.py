from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    full_name: Mapped[str] = mapped_column(String(200), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CostCentre(Base, TimestampMixin):
    __tablename__ = "cost_centres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(String(500), default="")
    owner: Mapped[str] = mapped_column(String(200), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Site(Base, TimestampMixin):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    address: Mapped[str] = mapped_column(String(500), default="")


class Floor(Base, TimestampMixin):
    __tablename__ = "floors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    name: Mapped[str] = mapped_column(String(100))
    level_no: Mapped[int] = mapped_column(Integer, default=0)
    ownership: Mapped[str] = mapped_column(String(20), default="own")  # own | rental
    customer_name: Mapped[str] = mapped_column(String(200), default="")


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"))
    name: Mapped[str] = mapped_column(String(100))
    is_rental: Mapped[bool] = mapped_column(Boolean, default=False)
    customer_name: Mapped[str] = mapped_column(String(200), default="")


class CableType(Base, TimestampMixin):
    __tablename__ = "cable_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    category: Mapped[str] = mapped_column(String(40), default="copper")
    connector_a: Mapped[str] = mapped_column(String(40), default="")
    connector_b: Mapped[str] = mapped_column(String(40), default="")
    default_color: Mapped[str] = mapped_column(String(40), default="#3366cc")
    supported_lengths: Mapped[str] = mapped_column(String(200), default="")


class ServiceType(Base, TimestampMixin):
    __tablename__ = "service_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    service_category: Mapped[str] = mapped_column(String(100), default="")
    bandwidth_profile: Mapped[str] = mapped_column(String(100), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class PortStatus(Base, TimestampMixin):
    __tablename__ = "port_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    color_hex: Mapped[str] = mapped_column(String(20), default="#888888")
    is_system_status: Mapped[bool] = mapped_column(Boolean, default=False)


class Rack(Base, TimestampMixin):
    __tablename__ = "racks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    cost_centre_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cost_centres.id"), nullable=True)
    floor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("floors.id"), nullable=True)
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(50), default="ODF")
    rack_type: Mapped[str] = mapped_column(String(50), default="Shelf")
    u_height: Mapped[int] = mapped_column(Integer, default=42)
    manufacturer: Mapped[str] = mapped_column(String(120), default="")
    model: Mapped[str] = mapped_column(String(120), default="")
    serial_number: Mapped[str] = mapped_column(String(120), default="")
    install_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    asset_tag: Mapped[str] = mapped_column(String(100), default="")
    power_feed: Mapped[str] = mapped_column(String(100), default="")
    notes: Mapped[str] = mapped_column(Text, default="")


class Cage(Base, TimestampMixin):
    __tablename__ = "cages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    cost_centre_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cost_centres.id"), nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(120), default="")
    model: Mapped[str] = mapped_column(String(120), default="")
    serial_number: Mapped[str] = mapped_column(String(120), default="")
    install_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    asset_tag: Mapped[str] = mapped_column(String(100), default="")
    notes: Mapped[str] = mapped_column(Text, default="")


class Shelf(Base, TimestampMixin):
    __tablename__ = "shelves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rack_id: Mapped[int] = mapped_column(ForeignKey("racks.id"))
    name: Mapped[str] = mapped_column(String(100))
    u_position: Mapped[int] = mapped_column(Integer, default=1)
    cost_centre_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cost_centres.id"), nullable=True)


class Panel(Base, TimestampMixin):
    __tablename__ = "panels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shelf_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shelves.id"), nullable=True)
    rack_id: Mapped[int] = mapped_column(ForeignKey("racks.id"))
    name: Mapped[str] = mapped_column(String(100))
    port_count: Mapped[int] = mapped_column(Integer, default=24)
    u_position: Mapped[int] = mapped_column(Integer, default=1)
    cost_centre_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cost_centres.id"), nullable=True)


class Device(Base, TimestampMixin):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rack_id: Mapped[int] = mapped_column(ForeignKey("racks.id"))
    name: Mapped[str] = mapped_column(String(120))
    device_type: Mapped[str] = mapped_column(String(80), default="switch")
    u_start: Mapped[int] = mapped_column(Integer, default=1)
    u_height: Mapped[int] = mapped_column(Integer, default=1)
    manufacturer: Mapped[str] = mapped_column(String(120), default="")
    model: Mapped[str] = mapped_column(String(120), default="")


class Port(Base, TimestampMixin):
    __tablename__ = "ports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    panel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("panels.id"), nullable=True)
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(80))
    port_number: Mapped[int] = mapped_column(Integer, default=1)
    connector_type: Mapped[str] = mapped_column(String(40), default="LC")
    status_id: Mapped[Optional[int]] = mapped_column(ForeignKey("port_statuses.id"), nullable=True)
    remark: Mapped[str] = mapped_column(Text, default="")


class Cable(Base, TimestampMixin):
    __tablename__ = "cables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cable_type_id: Mapped[int] = mapped_column(ForeignKey("cable_types.id"))
    service_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("service_types.id"), nullable=True)
    length_m: Mapped[float] = mapped_column(Float, default=0)
    color: Mapped[str] = mapped_column(String(40), default="")
    status: Mapped[str] = mapped_column(String(40), default="active")
    a_port_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ports.id"), nullable=True)
    b_port_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ports.id"), nullable=True)
    b_customer_name: Mapped[str] = mapped_column(String(200), default="")
    label: Mapped[str] = mapped_column(String(120), default="")
    notes: Mapped[str] = mapped_column(Text, default="")


class CableOrder(Base, TimestampMixin):
    __tablename__ = "cable_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_no: Mapped[str] = mapped_column(String(50), unique=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    cost_centre_id: Mapped[int] = mapped_column(ForeignKey("cost_centres.id"))
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    remarks: Mapped[str] = mapped_column(Text, default="")
    approver_comment: Mapped[str] = mapped_column(Text, default="")
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    lines = relationship("CableOrderLine", back_populates="order", cascade="all, delete-orphan")


class CableOrderLine(Base, TimestampMixin):
    __tablename__ = "cable_order_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("cable_orders.id"))
    line_no: Mapped[int] = mapped_column(Integer, default=1)
    cable_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cable_types.id"), nullable=True)
    service_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("service_types.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    path_group: Mapped[str] = mapped_column(String(50), default="A")
    path_index: Mapped[int] = mapped_column(Integer, default=1)
    endpoint_a: Mapped[str] = mapped_column(String(300), default="")
    endpoint_b: Mapped[str] = mapped_column(String(300), default="")
    a_port_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ports.id"), nullable=True)
    b_port_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ports.id"), nullable=True)
    requested_length_m: Mapped[float] = mapped_column(Float, default=0)
    routing_notes: Mapped[str] = mapped_column(Text, default="")

    order = relationship("CableOrder", back_populates="lines")


class ChangeRequest(Base, TimestampMixin):
    __tablename__ = "change_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_no: Mapped[str] = mapped_column(String(50), unique=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    change_type: Mapped[str] = mapped_column(String(40))
    target_entity_type: Mapped[str] = mapped_column(String(40))
    target_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    proposed_changes_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    required_approvals: Mapped[int] = mapped_column(Integer, default=1)
    applied: Mapped[bool] = mapped_column(Boolean, default=False)

    approvals = relationship(
        "ChangeRequestApproval", back_populates="change_request", cascade="all, delete-orphan"
    )


class ChangeRequestApproval(Base, TimestampMixin):
    __tablename__ = "change_request_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    change_request_id: Mapped[int] = mapped_column(ForeignKey("change_requests.id"))
    approver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[str] = mapped_column(String(20))  # approve | reject
    comment: Mapped[str] = mapped_column(Text, default="")
    decided_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    change_request = relationship("ChangeRequest", back_populates="approvals")


class TerminationRequest(Base, TimestampMixin):
    __tablename__ = "termination_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_no: Mapped[str] = mapped_column(String(50), unique=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    cable_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cables.id"), nullable=True)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cable_orders.id"), nullable=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="submitted")
    approver_comment: Mapped[str] = mapped_column(Text, default="")


class FloorPlan(Base, TimestampMixin):
    __tablename__ = "floor_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"), unique=True)
    scale_m_per_px: Mapped[float] = mapped_column(Float, default=0.05)
    canvas_data: Mapped[str] = mapped_column(Text, default="{}")

    segments = relationship("RouteSegment", back_populates="floor_plan", cascade="all, delete-orphan")


class RouteSegment(Base, TimestampMixin):
    __tablename__ = "route_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    floor_plan_id: Mapped[int] = mapped_column(ForeignKey("floor_plans.id"))
    start_x: Mapped[float] = mapped_column(Float, default=0)
    start_y: Mapped[float] = mapped_column(Float, default=0)
    end_x: Mapped[float] = mapped_column(Float, default=0)
    end_y: Mapped[float] = mapped_column(Float, default=0)
    path_length_m: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")

    floor_plan = relationship("FloorPlan", back_populates="segments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    role: Mapped[str] = mapped_column(String(40), default="")
    action: Mapped[str] = mapped_column(String(40), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    before_json: Mapped[str] = mapped_column(Text, default="")
    after_json: Mapped[str] = mapped_column(Text, default="")
    request_path: Mapped[str] = mapped_column(String(300), default="")
    ip_address: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class EmailOutbox(Base):
    __tablename__ = "email_outbox"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    to_address: Mapped[str] = mapped_column(String(200))
    subject: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text, default="")
    template: Mapped[str] = mapped_column(String(80), default="")
    related_entity: Mapped[str] = mapped_column(String(80), default="")
    related_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="simulated")
    sent_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class DwdmSystem(Base, TimestampMixin):
    __tablename__ = "dwdm_systems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")


class DwdmLink(Base, TimestampMixin):
    __tablename__ = "dwdm_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    system_id: Mapped[int] = mapped_column(ForeignKey("dwdm_systems.id"))
    name: Mapped[str] = mapped_column(String(120))
    site_a_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id"), nullable=True)
    site_b_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id"), nullable=True)
    distance_km: Mapped[float] = mapped_column(Float, default=0)
    fiber_path: Mapped[str] = mapped_column(String(300), default="")


class OpticalChannel(Base, TimestampMixin):
    __tablename__ = "optical_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("dwdm_links.id"))
    itu_channel: Mapped[str] = mapped_column(String(40), default="")
    wavelength_nm: Mapped[float] = mapped_column(Float, default=0)
    direction: Mapped[str] = mapped_column(String(20), default="bi")
    client_service: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(40), default="up")
    port_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ports.id"), nullable=True)
