from sqlalchemy.orm import Session

from app.services.scheduling_service import (
    find_available_slots,
    book_appointment,
)


def get_available_technician_slots(
    db: Session,
    zip_code: str,
    appliance_type: str,
):
    """
    Tool wrapper around scheduling service.

    Why have a separate tool layer?

    Because:
    - AI agent should not directly manipulate DB logic
    - tools provide clean interfaces for the agent
    - easier to extend later

    This tool returns simplified slot information
    that the AI can easily understand.
    """

    slots = find_available_slots(
        db=db,
        zip_code=zip_code,
        appliance_type=appliance_type,
    )

    formatted_slots = []

    for slot in slots:
        formatted_slots.append(
            {
                "slot_id": slot.id,
                "technician_id": slot.technician_id,
                "start_time": str(slot.start_time),
                "end_time": str(slot.end_time),
            }
        )

    return formatted_slots


def create_service_appointment(
    db: Session,
    slot_id: int,
    customer_name: str,
    customer_phone: str,
    zip_code: str,
    appliance_type: str,
    symptom_summary: str,
):
    """
    Tool used by AI agent to create technician appointment.
    """

    appointment = book_appointment(
        db=db,
        slot_id=slot_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        zip_code=zip_code,
        appliance_type=appliance_type,
        symptom_summary=symptom_summary,
    )

    if not appointment:
        return {
            "success": False,
            "message": "Selected appointment slot is no longer available."
        }

    return {
        "success": True,
        "appointment_id": appointment.id,
        "technician_id": appointment.technician_id,
    }