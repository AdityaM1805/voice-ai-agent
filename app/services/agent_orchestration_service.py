from datetime import datetime

from sqlalchemy.orm import Session

from app.agents.diagnostic_agent import extract_structured_information
from app.tools.scheduling_tools import (
    get_available_technician_slots,
    create_service_appointment,
)
from app.services.call_session_service import (
    get_or_create_call_session,
    update_call_session,
)
from app.services.notification_service import send_booking_confirmation_sms


def is_yes(message: str) -> bool:
    message = message.lower()
    return any(
        word in message
        for word in ["yes", "yeah", "yep", "sure", "confirm", "book it"]
    )


def is_no(message: str) -> bool:
    message = message.lower()
    return any(
        word in message
        for word in ["no", "not", "still", "doesn't", "didn't", "same issue"]
    )


def build_troubleshooting_response(appliance_type: str, symptoms: str) -> str:
    appliance = (appliance_type or "").lower()
    issue = (symptoms or "").lower()

    if appliance == "washer" and "leak" in issue:
        return (
            "Thanks. For a washer leak, please first check if the door is fully closed "
            "and if the inlet hoses behind the washer are tightly connected. "
            "Also check whether water is coming from underneath during the drain cycle. "
            "Did these steps solve the issue?"
        )

    if appliance == "refrigerator":
        return (
            "Thanks. Please check if the refrigerator door is sealing properly and whether "
            "the temperature setting was changed recently. "
            "Did these steps solve the issue?"
        )

    if appliance == "dryer":
        return (
            "Thanks. Please check if the lint filter is clean and whether the dryer vent "
            "has airflow. "
            "Did these steps solve the issue?"
        )

    return (
        "Thanks. Please try turning the appliance off for a minute, checking for any visible "
        "blockage or loose connection, and then turning it back on if it is safe. "
        "Did these steps solve the issue?"
    )


async def process_customer_message_logic(
    payload: dict,
    db: Session,
):
    call_sid = payload.get("call_sid", "demo-call")
    user_message = payload.get("message", "").strip()
    customer_phone = payload.get("customer_phone", "555-0000")

    session = get_or_create_call_session(
        db=db,
        call_sid=call_sid,
    )

    extracted_info = extract_structured_information(
        user_message=user_message,
    ) or {}

    session_updates = {}

    if extracted_info.get("appliance_type"):
        session_updates["appliance_type"] = extracted_info["appliance_type"]

    if extracted_info.get("zip_code"):
        session_updates["zip_code"] = extracted_info["zip_code"]

    if extracted_info.get("symptoms"):
        existing_symptoms = session.symptoms or ""
        new_symptoms = extracted_info["symptoms"]

        if new_symptoms.lower() not in existing_symptoms.lower():
            combined_symptoms = f"{existing_symptoms}. {new_symptoms}".strip(". ")
            session_updates["symptoms"] = combined_symptoms

    if session_updates:
        session = update_call_session(
            db=db,
            call_sid=call_sid,
            updates=session_updates,
        )

    stage = session.stage or "collect_issue"

    if stage == "collect_issue":
        if not session.appliance_type or not session.symptoms:
            return {
                "intent": "collect_issue",
                "assistant_response": (
                    "Please tell me which appliance is having trouble and what issue you are seeing."
                ),
            }

        if not session.zip_code:
            update_call_session(
                db=db,
                call_sid=call_sid,
                updates={"stage": "collect_zip"},
            )

            return {
                "intent": "collect_zip",
                "assistant_response": (
                    "Got it. What is the zip code where the appliance is located?"
                ),
            }

        update_call_session(
            db=db,
            call_sid=call_sid,
            updates={"stage": "troubleshooting"},
        )

        return {
            "intent": "troubleshooting",
            "assistant_response": build_troubleshooting_response(
                appliance_type=session.appliance_type,
                symptoms=session.symptoms,
            ),
        }

    if stage == "collect_zip":
        if not session.zip_code:
            return {
                "intent": "collect_zip",
                "assistant_response": (
                    "Could you please provide the zip code for the service location?"
                ),
            }

        update_call_session(
            db=db,
            call_sid=call_sid,
            updates={"stage": "troubleshooting"},
        )

        return {
            "intent": "troubleshooting",
            "assistant_response": build_troubleshooting_response(
                appliance_type=session.appliance_type,
                symptoms=session.symptoms,
            ),
        }

    if stage == "troubleshooting":
        if is_yes(user_message):
            update_call_session(
                db=db,
                call_sid=call_sid,
                updates={"stage": "completed"},
            )

            return {
                "intent": "resolved",
                "assistant_response": (
                    "Great, I’m glad that helped."
                ),
            }

        if is_no(user_message):
            update_call_session(
                db=db,
                call_sid=call_sid,
                updates={"stage": "offer_scheduling"},
            )

            return {
                "intent": "offer_scheduling",
                "assistant_response": (
                    "Thanks for trying that. Since the issue is still happening, "
                    "would you like me to schedule a technician appointment?"
                ),
            }

        return {
            "intent": "troubleshooting",
            "assistant_response": "Did those troubleshooting steps solve the issue?",
        }

    if stage == "offer_scheduling":
        if not is_yes(user_message):
            return {
                "intent": "offer_scheduling",
                "assistant_response": (
                    "No problem. Would you like me to schedule a technician appointment?"
                ),
            }

        slots = get_available_technician_slots(
            db=db,
            zip_code=session.zip_code,
            appliance_type=session.appliance_type,
        )

        if not slots:
            return {
                "intent": "scheduling",
                "assistant_response": (
                    "I could not find an available technician for your appliance and area right now."
                ),
            }

        first_slot = slots[0]

        slot_datetime = datetime.fromisoformat(str(first_slot["start_time"]))
        formatted_time = slot_datetime.strftime("%B %d at %I:%M %p")

        update_call_session(
            db=db,
            call_sid=call_sid,
            updates={
                "pending_slot_id": first_slot["slot_id"],
                "stage": "confirm_booking",
            },
        )

        return {
            "intent": "scheduling",
            "assistant_response": (
                f"I found an available technician appointment on {formatted_time}. "
                "Would you like to confirm this booking?"
            ),
            "available_slot": first_slot,
        }

    if stage == "confirm_booking":
        if not is_yes(user_message):
            return {
                "intent": "confirm_booking",
                "assistant_response": (
                    "No problem. I will not book the appointment unless you confirm."
                ),
            }

        appointment = create_service_appointment(
            db=db,
            slot_id=session.pending_slot_id,
            customer_name="Demo Customer",
            customer_phone=customer_phone,
            zip_code=session.zip_code,
            appliance_type=session.appliance_type,
            symptom_summary=session.symptoms or "",
        )

        if not appointment["success"]:
            return {
                "intent": "confirmation",
                "assistant_response": appointment["message"],
            }

        sms_sid = send_booking_confirmation_sms(
            to_phone_number=customer_phone,
            appointment_id=appointment["appointment_id"],
        )

        update_call_session(
            db=db,
            call_sid=call_sid,
            updates={
                "pending_slot_id": None,
                "stage": "completed",
            },
        )

        return {
            "intent": "confirmation",
            "assistant_response": "Your technician appointment has been successfully booked.",
            "appointment_details": appointment,
            "notification": {
                "sms_sent": sms_sid is not None,
                "sms_sid": sms_sid,
            },
        }

    return {
        "intent": "completed",
        "assistant_response": "Thank you for calling Sears Home Services.",
    }