from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.scheduling_service import find_available_slots
from app.agents.diagnostic_agent import (
    generate_diagnostic_response,
    detect_customer_intent,
    extract_structured_information,
)
from app.tools.scheduling_tools import (
    get_available_technician_slots,
    create_service_appointment,
)
from app.services.call_session_service import (
    get_or_create_call_session,
    update_call_session,
)


app = FastAPI(
    title="SHS Voice AI Agent",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SHS Voice AI Agent",
    }


@app.get("/config-check")
async def config_check():
    return {
        "database_url": settings.DATABASE_URL,
        "twilio_phone_number": settings.TWILIO_PHONE_NUMBER,
    }


@app.get("/test/available-slots")
async def test_available_slots(
    zip_code: str,
    appliance_type: str,
    db: Session = Depends(get_db),
):
    slots = find_available_slots(
        db=db,
        zip_code=zip_code,
        appliance_type=appliance_type,
    )

    return [
        {
            "slot_id": slot.id,
            "technician_id": slot.technician_id,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        }
        for slot in slots
    ]


@app.post("/test/diagnostic-agent")
async def test_diagnostic_agent(payload: dict):
    user_message = payload.get("message", "")
    conversation_context = payload.get("context", {})

    assistant_response = generate_diagnostic_response(
        user_message=user_message,
        conversation_context=conversation_context,
    )

    return {
        "assistant_response": assistant_response,
    }


@app.post("/agent/process")
async def process_customer_message(
    payload: dict,
    db: Session = Depends(get_db),
):
    call_sid = payload.get("call_sid", "demo-call")
    user_message = payload.get("message", "")

    session = get_or_create_call_session(
        db=db,
        call_sid=call_sid,
    )

    conversation_context = {
        "appliance_type": session.appliance_type,
        "symptoms": session.symptoms,
        "zip_code": session.zip_code,
    }

    intent = detect_customer_intent(user_message)

    extracted_info = extract_structured_information(
        user_message=user_message,
    )

    session_updates = {}

    if extracted_info.get("appliance_type"):
        session_updates["appliance_type"] = extracted_info["appliance_type"]

    if extracted_info.get("zip_code"):
        session_updates["zip_code"] = extracted_info["zip_code"]

    if extracted_info.get("symptoms"):
        session_updates["symptoms"] = extracted_info["symptoms"]

    if session_updates:
        session = update_call_session(
            db=db,
            call_sid=call_sid,
            updates=session_updates,
        )

        conversation_context = {
            "appliance_type": session.appliance_type,
            "symptoms": session.symptoms,
            "zip_code": session.zip_code,
        }

    if intent == "emergency":
        return {
            "intent": intent,
            "assistant_response": (
                "For safety reasons, please stop using the appliance immediately. "
                "I recommend scheduling a technician as soon as possible."
            ),
        }

    if intent == "scheduling":
        if not session.zip_code or not session.appliance_type:
            return {
                "intent": intent,
                "assistant_response": (
                    "Before I schedule a technician, could you provide your zip code "
                    "and appliance type?"
                ),
            }

        slots = get_available_technician_slots(
            db=db,
            zip_code=session.zip_code,
            appliance_type=session.appliance_type,
        )

        if not slots:
            return {
                "intent": intent,
                "assistant_response": (
                    "I could not find any available technicians for your appliance "
                    "and area right now."
                ),
            }

        first_slot = slots[0]

        session = update_call_session(
            db=db,
            call_sid=call_sid,
            updates={
                "pending_slot_id": first_slot["slot_id"],
            },
        )

        return {
            "intent": intent,
            "assistant_response": (
                f"I found an available technician appointment on "
                f"{first_slot['start_time']}. "
                "Would you like to confirm this booking?"
            ),
            "available_slot": first_slot,
        }

    if intent == "confirmation":
        if not session.pending_slot_id:
            return {
                "intent": intent,
                "assistant_response": (
                    "I do not currently have a pending appointment to confirm."
                ),
            }

        appointment = create_service_appointment(
            db=db,
            slot_id=session.pending_slot_id,
            customer_name="Demo Customer",
            customer_phone="555-0000",
            zip_code=session.zip_code,
            appliance_type=session.appliance_type,
            symptom_summary=session.symptoms or "",
        )

        if not appointment["success"]:
            return {
                "intent": intent,
                "assistant_response": appointment["message"],
            }

        update_call_session(
            db=db,
            call_sid=call_sid,
            updates={
                "pending_slot_id": None,
            },
        )

        return {
            "intent": intent,
            "assistant_response": (
                "Your technician appointment has been successfully booked."
            ),
            "appointment_details": appointment,
        }

    assistant_response = generate_diagnostic_response(
        user_message=user_message,
        conversation_context=conversation_context,
    )

    return {
        "intent": intent,
        "assistant_response": assistant_response,
    }