from sqlalchemy.orm import Session

from app.models import CallSession


def get_or_create_call_session(
    db: Session,
    call_sid: str,
):
    """
    Retrieve existing call session.

    If session does not exist,
    create a new one.

    This helps maintain conversation memory
    across multiple customer interactions.
    """

    session = (
        db.query(CallSession)
        .filter(CallSession.call_sid == call_sid)
        .first()
    )

    if session:
        return session

    session = CallSession(
        call_sid=call_sid
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def update_call_session(
    db: Session,
    call_sid: str,
    updates: dict,
):
    """
    Update stored conversation memory.

    Example:
    {
        "appliance_type": "washer",
        "zip_code": "95112"
    }
    """

    session = (
        db.query(CallSession)
        .filter(CallSession.call_sid == call_sid)
        .first()
    )

    if not session:
        return None

    for key, value in updates.items():
        setattr(session, key, value)

    db.commit()
    db.refresh(session)

    return session