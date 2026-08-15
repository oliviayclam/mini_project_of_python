from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str

    class Config:
        from_attributes = True


class LoginForm(BaseModel):
    username: str
    password: str


class CostCentreIn(BaseModel):
    code: str
    name: str
    address: str = ""
    owner: str = ""
    active: bool = True


class CostCentreOut(CostCentreIn):
    id: int

    class Config:
        from_attributes = True


class SiteIn(BaseModel):
    name: str
    code: str
    address: str = ""


class SiteOut(SiteIn):
    id: int

    class Config:
        from_attributes = True


class FloorIn(BaseModel):
    site_id: int
    name: str
    level_no: int = 0
    ownership: str = "own"
    customer_name: str = ""


class FloorOut(FloorIn):
    id: int

    class Config:
        from_attributes = True


class RoomIn(BaseModel):
    floor_id: int
    name: str
    is_rental: bool = False
    customer_name: str = ""


class RoomOut(RoomIn):
    id: int

    class Config:
        from_attributes = True


class CableTypeIn(BaseModel):
    name: str
    category: str = "copper"
    connector_a: str = ""
    connector_b: str = ""
    default_color: str = "#3366cc"
    supported_lengths: str = ""


class CableTypeOut(CableTypeIn):
    id: int

    class Config:
        from_attributes = True


class ServiceTypeIn(BaseModel):
    name: str
    service_category: str = ""
    bandwidth_profile: str = ""
    active: bool = True


class ServiceTypeOut(ServiceTypeIn):
    id: int

    class Config:
        from_attributes = True


class PortStatusIn(BaseModel):
    name: str
    color_hex: str = "#888888"
    is_system_status: bool = False


class PortStatusOut(PortStatusIn):
    id: int

    class Config:
        from_attributes = True


class RackIn(BaseModel):
    name: str
    cost_centre_id: Optional[int] = None
    floor_id: Optional[int] = None
    room_id: Optional[int] = None
    asset_type: str = "ODF"
    rack_type: str = "Shelf"
    u_height: int = 42
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    install_date: Optional[date] = None
    expire_date: Optional[date] = None
    asset_tag: str = ""
    power_feed: str = ""
    notes: str = ""


class RackOut(RackIn):
    id: int

    class Config:
        from_attributes = True


class CageIn(BaseModel):
    name: str
    room_id: Optional[int] = None
    cost_centre_id: Optional[int] = None
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    install_date: Optional[date] = None
    expire_date: Optional[date] = None
    asset_tag: str = ""
    notes: str = ""


class CageOut(CageIn):
    id: int

    class Config:
        from_attributes = True


class ShelfIn(BaseModel):
    rack_id: int
    name: str
    u_position: int = 1
    cost_centre_id: Optional[int] = None


class ShelfOut(ShelfIn):
    id: int

    class Config:
        from_attributes = True


class PanelIn(BaseModel):
    rack_id: int
    name: str
    shelf_id: Optional[int] = None
    port_count: int = 24
    u_position: int = 1
    cost_centre_id: Optional[int] = None
    create_ports: bool = True


class PanelOut(BaseModel):
    id: int
    rack_id: int
    shelf_id: Optional[int]
    name: str
    port_count: int
    u_position: int
    cost_centre_id: Optional[int]

    class Config:
        from_attributes = True


class DeviceIn(BaseModel):
    rack_id: int
    name: str
    device_type: str = "switch"
    u_start: int = 1
    u_height: int = 1
    manufacturer: str = ""
    model: str = ""


class DeviceOut(DeviceIn):
    id: int

    class Config:
        from_attributes = True


class PortOut(BaseModel):
    id: int
    panel_id: Optional[int]
    device_id: Optional[int]
    name: str
    port_number: int
    connector_type: str
    status_id: Optional[int]
    remark: str

    class Config:
        from_attributes = True


class PortRemarkIn(BaseModel):
    remark: str


class PortStatusUpdateIn(BaseModel):
    status_id: int


class CableIn(BaseModel):
    cable_type_id: int
    service_type_id: Optional[int] = None
    length_m: float = 0
    color: str = ""
    status: str = "active"
    a_port_id: Optional[int] = None
    b_port_id: Optional[int] = None
    b_customer_name: str = ""
    label: str = ""
    notes: str = ""


class CableOut(CableIn):
    id: int

    class Config:
        from_attributes = True


class OrderLineIn(BaseModel):
    line_no: int = 1
    cable_type_id: Optional[int] = None
    service_type_id: Optional[int] = None
    quantity: int = 1
    path_group: str = "A"
    path_index: int = 1
    endpoint_a: str = ""
    endpoint_b: str = ""
    a_port_id: Optional[int] = None
    b_port_id: Optional[int] = None
    requested_length_m: float = 0
    routing_notes: str = ""


class OrderLineOut(OrderLineIn):
    id: int
    order_id: int

    class Config:
        from_attributes = True


class OrderIn(BaseModel):
    cost_centre_id: int
    remarks: str = ""
    lines: list[OrderLineIn] = Field(default_factory=list)


class OrderOut(BaseModel):
    id: int
    request_no: str
    vendor_id: int
    cost_centre_id: int
    status: str
    remarks: str
    approver_comment: str
    lines: list[OrderLineOut] = []

    class Config:
        from_attributes = True


class CommentIn(BaseModel):
    comment: str = ""


class ChangeRequestIn(BaseModel):
    change_type: str
    target_entity_type: str
    target_entity_id: Optional[int] = None
    proposed_changes: dict[str, Any] = Field(default_factory=dict)
    required_approvals: int = 1


class ChangeApprovalOut(BaseModel):
    id: int
    approver_id: int
    decision: str
    comment: str
    decided_at: datetime

    class Config:
        from_attributes = True


class ChangeRequestOut(BaseModel):
    id: int
    request_no: str
    requester_id: int
    change_type: str
    target_entity_type: str
    target_entity_id: Optional[int]
    proposed_changes_json: str
    status: str
    required_approvals: int
    applied: bool
    approvals: list[ChangeApprovalOut] = []

    class Config:
        from_attributes = True


class TerminationIn(BaseModel):
    cable_id: Optional[int] = None
    order_id: Optional[int] = None
    reason: str = ""


class TerminationOut(BaseModel):
    id: int
    request_no: str
    requester_id: int
    cable_id: Optional[int]
    order_id: Optional[int]
    reason: str
    status: str
    approver_comment: str

    class Config:
        from_attributes = True


class FloorPlanIn(BaseModel):
    scale_m_per_px: float = 0.05
    canvas_data: str = "{}"


class SegmentIn(BaseModel):
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    notes: str = ""


class SegmentOut(SegmentIn):
    id: int
    path_length_m: float

    class Config:
        from_attributes = True


class FloorPlanOut(BaseModel):
    id: int
    floor_id: int
    scale_m_per_px: float
    canvas_data: str
    segments: list[SegmentOut] = []

    class Config:
        from_attributes = True


class AuditOut(BaseModel):
    id: int
    user_id: Optional[int]
    role: str
    action: str
    entity_type: str
    entity_id: Optional[str]
    before_json: str
    after_json: str
    request_path: str
    ip_address: str
    created_at: datetime

    class Config:
        from_attributes = True


class AssetCreateIn(BaseModel):
    cost_centre_id: int
    floor_id: int
    room_id: int
    name: str
    rack_id: Optional[int] = None
    shelf_or_u: int = 1
    port_count: int = 24
    asset_type: str = "ODF"
    rack_type: str = "Shelf"
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    install_date: Optional[date] = None
    expire_date: Optional[date] = None
    asset_tag: str = ""
    notes: str = ""
    device_name: Optional[str] = None
    cable_type_id: Optional[int] = None


class StructuredCableIn(BaseModel):
    cable_type_id: int
    service_type_id: Optional[int] = None
    a_port_id: int
    b_port_id: Optional[int] = None
    b_customer_name: str = ""
    length_m: float = 0
    label: str = ""
    notes: str = ""


class SuggestionOut(BaseModel):
    cable_type_id: Optional[int] = None
    cable_type_name: Optional[str] = None
    service_type_id: Optional[int] = None
    service_type_name: Optional[str] = None
    estimated_length_m: float = 0
    notes: str = ""


class DwdmSystemIn(BaseModel):
    name: str
    description: str = ""


class DwdmSystemOut(DwdmSystemIn):
    id: int

    class Config:
        from_attributes = True


class DwdmLinkIn(BaseModel):
    system_id: int
    name: str
    site_a_id: Optional[int] = None
    site_b_id: Optional[int] = None
    distance_km: float = 0
    fiber_path: str = ""


class DwdmLinkOut(DwdmLinkIn):
    id: int

    class Config:
        from_attributes = True


class OpticalChannelIn(BaseModel):
    link_id: int
    itu_channel: str = ""
    wavelength_nm: float = 0
    direction: str = "bi"
    client_service: str = ""
    status: str = "up"
    port_id: Optional[int] = None


class OpticalChannelOut(OpticalChannelIn):
    id: int

    class Config:
        from_attributes = True
