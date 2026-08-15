from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import ROLE_ADMIN, get_current_user, require_roles
from app.models import DwdmLink, DwdmSystem, OpticalChannel, User
from app.schemas import (
    DwdmLinkIn,
    DwdmLinkOut,
    DwdmSystemIn,
    DwdmSystemOut,
    OpticalChannelIn,
    OpticalChannelOut,
)
from app.services.audit import write_audit

router = APIRouter(prefix="/dwdm", tags=["dwdm"])


@router.get("/systems", response_model=list[DwdmSystemOut])
def list_systems(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(DwdmSystem).all()


@router.post("/systems", response_model=DwdmSystemOut)
def create_system(
    payload: DwdmSystemIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
):
    row = DwdmSystem(**payload.model_dump())
    db.add(row)
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="dwdm_system",
        entity_id=None,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(row)
    return row


@router.get("/links", response_model=list[DwdmLinkOut])
def list_links(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(DwdmLink).all()


@router.post("/links", response_model=DwdmLinkOut)
def create_link(
    payload: DwdmLinkIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
):
    row = DwdmLink(**payload.model_dump())
    db.add(row)
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="dwdm_link",
        entity_id=None,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(row)
    return row


@router.get("/channels", response_model=list[OpticalChannelOut])
def list_channels(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(OpticalChannel).all()


@router.post("/channels", response_model=OpticalChannelOut)
def create_channel(
    payload: OpticalChannelIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(ROLE_ADMIN))],
):
    row = OpticalChannel(**payload.model_dump())
    db.add(row)
    write_audit(
        db,
        user_id=user.id,
        role=user.role,
        action="create",
        entity_type="optical_channel",
        entity_id=None,
        after=payload.model_dump(),
        request_path=str(request.url.path),
    )
    db.commit()
    db.refresh(row)
    return row
