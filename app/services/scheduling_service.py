from sqlalchemy.orm import Session

from app.models import (
    Technician,
    ServiceArea,
    Specialty,
    AvailabilitySlot,
    Appointment,
)


def find_available_slots(
    db: Session,
    zip_code: str,
    appliance_type: str,
):
    """
    Find available technician slots based on:
    1. Customer zip code
    2. Appliance type
    3. Slot not already booked

    Example:
    Customer says:
    - zip code = 95112
    - appliance = washer

    We only return technicians who:
    - serve 95112
    - repair washers
    - have open appointment slots
    """

    normalized_appliance_type = appliance_type.lower().strip()

    available_slots = (
        db.query(AvailabilitySlot)
        .join(Technician, AvailabilitySlot.technician_id == Technician.id)
        .join(ServiceArea, ServiceArea.technician_id == Technician.id)
        .join(Specialty, Specialty.technician_id == Technician.id)
        .filter(ServiceArea.zip_code == zip_code)
        .filter(Specialty.appliance_type == normalized_appliance_type)
        .filter(AvailabilitySlot.is_booked == False)
        .filter(Technician.is_active == True)
        .order_by(AvailabilitySlot.start_time.asc())
        .all()
    )

    return available_slots


def book_appointment(
    db: Session,
    slot_id: int,
    customer_name: str,
    customer_phone: str,
    zip_code: str,
    appliance_type: str,
    symptom_summary: str,
):
    """
    Book a technician appointment for a selected available slot.

    Important:
    We first check if the slot exists and is still available.
    This prevents double-booking.
    """

    slot = (
        db.query(AvailabilitySlot)
        .filter(AvailabilitySlot.id == slot_id)
        .filter(AvailabilitySlot.is_booked == False)
        .first()
    )

    if not slot:
        return None

    appointment = Appointment(
        customer_name=customer_name,
        customer_phone=customer_phone,
        zip_code=zip_code,
        appliance_type=appliance_type.lower().strip(),
        symptom_summary=symptom_summary,
        technician_id=slot.technician_id,
        availability_slot_id=slot.id,
    )

    slot.is_booked = True

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment