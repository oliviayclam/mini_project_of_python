import smtplib
from email.message import EmailMessage
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import EmailOutbox
from app.services.audit import write_audit


def send_email(
    db: Session,
    *,
    to_address: str,
    subject: str,
    body: str,
    template: str = "",
    related_entity: str = "",
    related_id: Optional[str] = None,
    user_id: Optional[int] = None,
    role: str = "",
) -> EmailOutbox:
    status = "simulated"
    if settings.smtp_host:
        try:
            msg = EmailMessage()
            msg["From"] = settings.mail_from
            msg["To"] = to_address
            msg["Subject"] = subject
            msg.set_content(body)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                if settings.smtp_user:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            status = "sent"
        except Exception as exc:  # noqa: BLE001
            status = f"failed:{exc}"
            print(f"[email failed] {to_address}: {exc}")
    else:
        print(f"[email simulated] To={to_address} Subject={subject}\n{body}\n")

    row = EmailOutbox(
        to_address=to_address,
        subject=subject,
        body=body,
        template=template,
        related_entity=related_entity,
        related_id=related_id,
        status=status,
    )
    db.add(row)
    write_audit(
        db,
        user_id=user_id,
        role=role,
        action="email_sent",
        entity_type=related_entity or "email",
        entity_id=related_id,
        after={"to": to_address, "subject": subject, "status": status},
    )
    db.flush()
    return row


def notify_workflow(
    db: Session,
    *,
    event: str,
    to_address: str,
    entity_label: str,
    request_no: str,
    detail: str = "",
    user_id: Optional[int] = None,
    role: str = "",
) -> None:
    subjects = {
        "submit": f"[Pending] {entity_label} {request_no} submitted",
        "pending": f"[Action required] Approve {entity_label} {request_no}",
        "approve": f"[Approved] {entity_label} {request_no}",
        "reject": f"[Rejected] {entity_label} {request_no}",
    }
    subject = subjects.get(event, f"[{event}] {entity_label} {request_no}")
    body = f"{entity_label} {request_no}\nEvent: {event}\n{detail}".strip()
    send_email(
        db,
        to_address=to_address,
        subject=subject,
        body=body,
        template=event,
        related_entity=entity_label,
        related_id=request_no,
        user_id=user_id,
        role=role,
    )
